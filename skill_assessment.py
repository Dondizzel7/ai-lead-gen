"""
Skill Assessment Module for AI Candidate Evaluation Framework

This module evaluates practical skills through coding challenges, problem-solving exercises,
and domain knowledge verification to ensure candidates have the technical abilities required for the role.
"""

import logging
import os
import json
import time
import subprocess
import tempfile
import re
from typing import Dict, List, Any, Optional
import docker

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestCasesRepository:
    """Repository of test cases for coding challenges."""
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the test cases repository.
        
        Args:
            data_path: Path to test cases data files
        """
        self.data_path = data_path or os.path.join(os.path.dirname(__file__), 'data')
        self.test_cases = {}
        
        # Load test cases from data files
        self._load_test_cases()
        
        logger.info(f"Test cases repository initialized with {len(self.test_cases)} challenges")
    
    def _load_test_cases(self):
        """Load test cases from data files."""
        try:
            # In a real implementation, this would load from actual data files
            # For this example, we'll use mock data
            
            # Example test cases for different challenges
            self.test_cases = {
                # String manipulation challenge
                "reverse_string": [
                    {"input": "hello", "expected_output": "olleh"},
                    {"input": "world", "expected_output": "dlrow"},
                    {"input": "a", "expected_output": "a"},
                    {"input": "", "expected_output": ""}
                ],
                
                # Array challenge
                "find_max": [
                    {"input": [1, 2, 3, 4, 5], "expected_output": 5},
                    {"input": [-1, -2, -3], "expected_output": -1},
                    {"input": [0], "expected_output": 0},
                    {"input": [], "expected_output": None}
                ],
                
                # Algorithm challenge
                "fibonacci": [
                    {"input": 0, "expected_output": 0},
                    {"input": 1, "expected_output": 1},
                    {"input": 5, "expected_output": 5},
                    {"input": 10, "expected_output": 55}
                ],
                
                # Data structure challenge
                "balanced_parentheses": [
                    {"input": "()", "expected_output": True},
                    {"input": "()[]{}", "expected_output": True},
                    {"input": "(]", "expected_output": False},
                    {"input": "([)]", "expected_output": False},
                    {"input": "{[]}", "expected_output": True}
                ]
            }
            
        except Exception as e:
            logger.error(f"Error loading test cases: {str(e)}")
            self.test_cases = {}
    
    def get_test_cases(self, challenge_id: str) -> List[Dict[str, Any]]:
        """
        Get test cases for a specific challenge.
        
        Args:
            challenge_id: Identifier for the coding challenge
            
        Returns:
            List of test cases
        """
        return self.test_cases.get(challenge_id, [])
    
    def get_challenge_ids(self) -> List[str]:
        """
        Get all available challenge IDs.
        
        Returns:
            List of challenge IDs
        """
        return list(self.test_cases.keys())


class LanguageAnalyzer:
    """Base class for language-specific code analyzers."""
    
    def __init__(self):
        """Initialize the language analyzer."""
        pass
    
    def execute(self, code: str, input_data: Any) -> Any:
        """
        Execute code with the given input.
        
        Args:
            code: Source code to execute
            input_data: Input data for the code
            
        Returns:
            Execution output
        """
        raise NotImplementedError("Subclasses must implement execute method")
    
    def analyze_quality(self, code: str) -> Dict[str, float]:
        """
        Analyze code quality.
        
        Args:
            code: Source code to analyze
            
        Returns:
            Code quality metrics
        """
        raise NotImplementedError("Subclasses must implement analyze_quality method")
    
    def get_memory_usage(self) -> int:
        """
        Get memory usage of the last execution.
        
        Returns:
            Memory usage in bytes
        """
        return 0  # Default implementation


class PythonAnalyzer(LanguageAnalyzer):
    """Analyzer for Python code."""
    
    def __init__(self):
        """Initialize the Python analyzer."""
        super().__init__()
        self.last_memory_usage = 0
        
        # Check if Docker is available
        try:
            self.docker_client = docker.from_env()
            self.use_docker = True
            logger.info("Docker is available, will use containerized execution")
        except Exception as e:
            logger.warning(f"Docker not available: {str(e)}. Will use subprocess for execution.")
            self.use_docker = False
    
    def execute(self, code: str, input_data: Any) -> Any:
        """
        Execute Python code with the given input.
        
        Args:
            code: Python source code
            input_data: Input data for the code
            
        Returns:
            Execution output
        """
        # Prepare input data as JSON string
        input_json = json.dumps(input_data)
        
        # Wrap code to handle input and output
        wrapped_code = f"""
import json
import sys
import traceback
import resource

# Load input data
input_data = json.loads('{input_json}')

# Original code
{code}

# Assume the last function or class defined is the solution
# Get all defined functions
function_names = [name for name in locals() if callable(locals()[name]) and not name.startswith('__')]
if function_names:
    # Call the last defined function with input data
    result = locals()[function_names[-1]](input_data)
    print(json.dumps(result))
else:
    # If no function defined, assume the code directly processes input_data
    # and assigns result to a variable named 'result'
    if 'result' in locals():
        print(json.dumps(result))
    else:
        print(json.dumps(None))

# Get memory usage
usage = resource.getrusage(resource.RUSAGE_SELF)
print(f"MEMORY_USAGE: {{usage.ru_maxrss}}", file=sys.stderr)
"""
        
        if self.use_docker:
            return self._execute_with_docker(wrapped_code)
        else:
            return self._execute_with_subprocess(wrapped_code)
    
    def _execute_with_docker(self, code: str) -> Any:
        """Execute code in a Docker container."""
        try:
            # Create a temporary file with the code
            with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
                f.write(code.encode('utf-8'))
                temp_file = f.name
            
            # Run the code in a Docker container
            container = self.docker_client.containers.run(
                'python:3.9-slim',
                f'python {os.path.basename(temp_file)}',
                volumes={os.path.dirname(temp_file): {'bind': '/app', 'mode': 'ro'}},
                working_dir='/app',
                stderr=True,
                stdout=True,
                detach=True,
                remove=True,
                mem_limit='128m',
                network_disabled=True,
                cap_drop=['ALL'],
                security_opt=['no-new-privileges']
            )
            
            # Wait for execution to complete (with timeout)
            result = container.wait(timeout=10)
            
            # Get output
            output = container.logs().decode('utf-8')
            
            # Clean up
            os.unlink(temp_file)
            
            # Check for errors
            if result['StatusCode'] != 0:
                raise Exception(f"Execution failed: {output}")
            
            # Extract memory usage
            memory_match = re.search(r'MEMORY_USAGE: (\d+)', output)
            if memory_match:
                self.last_memory_usage = int(memory_match.group(1))
            
            # Parse output as JSON
            output_lines = output.strip().split('\n')
            if output_lines:
                try:
                    return json.loads(output_lines[0])
                except json.JSONDecodeError:
                    return output_lines[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Docker execution error: {str(e)}")
            return str(e)
    
    def _execute_with_subprocess(self, code: str) -> Any:
        """Execute code using subprocess."""
        try:
            # Create a temporary file with the code
            with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
                f.write(code.encode('utf-8'))
                temp_file = f.name
            
            # Run the code as a subprocess
            process = subprocess.Popen(
                ['python', temp_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for execution to complete (with timeout)
            stdout, stderr = process.communicate(timeout=5)
            
            # Clean up
            os.unlink(temp_file)
            
            # Check for errors
            if process.returncode != 0:
                raise Exception(f"Execution failed: {stderr}")
            
            # Extract memory usage
            memory_match = re.search(r'MEMORY_USAGE: (\d+)', stderr)
            if memory_match:
                self.last_memory_usage = int(memory_match.group(1))
            
            # Parse output as JSON
            output_lines = stdout.strip().split('\n')
            if output_lines:
                try:
                    return json.loads(output_lines[0])
                except json.JSONDecodeError:
                    return output_lines[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Subprocess execution error: {str(e)}")
            return str(e)
    
    def analyze_quality(self, code: str) -> Dict[str, float]:
        """
        Analyze Python code quality.
        
        Args:
            code: Python source code
            
        Returns:
            Code quality metrics
        """
        # In a real implementation, this would use tools like pylint, flake8, etc.
        # For this example, we'll use simple heuristics
        
        # Count lines of code
        lines = code.strip().split('\n')
        loc = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
        
        # Check for comments
        comment_lines = len([line for line in lines if line.strip().startswith('#')])
        comment_ratio = comment_lines / max(1, loc)
        
        # Check for docstrings
        docstring_count = len(re.findall(r'""".*?"""', code, re.DOTALL))
        has_docstrings = docstring_count > 0
        
        # Check for function length
        function_bodies = re.findall(r'def\s+\w+\s*\(.*?\).*?:(.*?)(?=\n\S|\Z)', code, re.DOTALL)
        avg_function_length = sum(len(body.strip().split('\n')) for body in function_bodies) / max(1, len(function_bodies))
        
        # Check for complexity indicators
        complexity_indicators = ['for', 'while', 'if', 'elif', 'else', 'try', 'except', 'with', 'lambda']
        complexity_count = sum(len(re.findall(r'\b' + indicator + r'\b', code)) for indicator in complexity_indicators)
        complexity_ratio = complexity_count / max(1, loc)
        
        # Calculate metrics
        complexity = min(1.0, complexity_ratio * 2)  # Higher is more complex
        maintainability = min(1.0, (comment_ratio * 0.5) + (0.3 if has_docstrings else 0) + (0.2 if avg_function_length < 15 else 0))
        efficiency = max(0.0, 1.0 - (complexity * 0.5))
        best_practices = min(1.0, maintainability * 0.7 + (0.3 if complexity < 0.5 else 0))
        
        # Overall quality score
        overall = (
            (1.0 - complexity) * 0.3 +
            maintainability * 0.3 +
            efficiency * 0.2 +
            best_practices * 0.2
        )
        
        return {
            "complexity": complexity,
            "maintainability": maintainability,
            "efficiency": efficiency,
            "best_practices": best_practices,
            "overall": overall
        }
    
    def get_memory_usage(self) -> int:
        """
        Get memory usage of the last execution.
        
        Returns:
            Memory usage in bytes
        """
        return self.last_memory_usage


class JavaScriptAnalyzer(LanguageAnalyzer):
    """Analyzer for JavaScript code."""
    
    def __init__(self):
        """Initialize the JavaScript analyzer."""
        super().__init__()
        self.last_memory_usage = 0
        
        # Check if Docker is available
        try:
            self.docker_client = docker.from_env()
            self.use_docker = True
            logger.info("Docker is available, will use containerized execution")
        except Exception as e:
            logger.warning(f"Docker not available: {str(e)}. Will use subprocess for execution.")
            self.use_docker = False
    
    def execute(self, code: str, input_data: Any) -> Any:
        """
        Execute JavaScript code with the given input.
        
        Args:
            code: JavaScript source code
            input_data: Input data for the code
            
        Returns:
            Execution output
        """
        # Prepare input data as JSON string
        input_json = json.dumps(input_data)
        
        # Wrap code to handle input and output
        wrapped_code = f"""
// Load input data
const inputData = {input_json};

// Original code
{code}

// Get all defined functions
const functionNames = Object.keys(global).filter(name => 
    typeof global[name] === 'function' && 
    !name.startsWith('_') && 
    ['require', 'console', 'setTimeout', 'setInterval', 'setImmediate', 'clearTimeout', 'clearInterval', 'clearImmediate'].indexOf(name) === -1
);

if (functionNames.length > 0) {{
    // Call the last defined function with input data
    const result = global[functionNames[functionNames.length - 1]](inputData);
    console.log(JSON.stringify(result));
}} else {{
    // If no function defined, assume the code directly processes inputData
    // and assigns result to a variable named 'result'
    if (typeof result !== 'undefined') {{
        console.log(JSON.stringify(result));
    }} else {{
        console.log(JSON.stringify(null));
    }}
}}

// Get memory usage
const memoryUsage = process.memoryUsage();
console.error(`MEMORY_USAGE: ${{memoryUsage.heapUsed}}`);
"""
        
        if self.use_docker:
            return self._execute_with_docker(wrapped_code)
        else:
            return self._execute_with_subprocess(wrapped_code)
    
    def _execute_with_docker(self, code: str) -> Any:
        """Execute code in a Docker container."""
        try:
            # Create a temporary file with the code
            with tempfile.NamedTemporaryFile(suffix='.js', delete=False) as f:
                f.write(code.encode('utf-8'))
                temp_file = f.name
            
            # Run the code in a Docker container
            container = self.docker_client.containers.run(
                'node:14-alpine',
                f'node {os.path.basename(temp_file)}',
                volumes={os.path.dirname(temp_file): {'bind': '/app', 'mode': 'ro'}},
                working_dir='/app',
                stderr=True,
                stdout=True,
                detach=True,
                remove=True,
                mem_limit='128m',
                network_disabled=True,
                cap_drop=['ALL'],
                security_opt=['no-new-privileges']
            )
            
            # Wait for execution to complete (with timeout)
            result = container.wait(timeout=10)
            
            # Get output
            output = container.logs().decode('utf-8')
            
            # Clean up
            os.unlink(temp_file)
            
            # Check for errors
            if result['StatusCode'] != 0:
                raise Exception(f"Execution failed: {output}")
            
            # Extract memory usage
            memory_match = re.search(r'MEMORY_USAGE: (\d+)', output)
            if memory_match:
                self.last_memory_usage = int(memory_match.group(1))
            
            # Parse output as JSON
            output_lines = output.strip().split('\n')
            if output_lines:
                try:
                    return json.loads(output_lines[0])
                except json.JSONDecodeError:
                    return output_lines[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Docker execution error: {str(e)}")
            return str(e)
    
    def _execute_with_subprocess(self, code: str) -> Any:
        """Execute code using subprocess."""
        try:
            # Create a temporary file with the code
            with tempfile.NamedTemporaryFile(suffix='.js', delete=False) as f:
                f.write(code.encode('utf-8'))
                temp_file = f.name
            
            # Run the code as a subprocess
            process = subprocess.Popen(
                ['node', temp_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for execution to complete (with timeout)
            stdout, stderr = process.communicate(timeout=5)
            
            # Clean up
            os.unlink(temp_file)
            
            # Check for errors
            if process.returncode != 0:
                raise Exception(f"Execution failed: {stderr}")
            
            # Extract memory usage
            memory_match = re.search(r'MEMORY_USAGE: (\d+)', stderr)
            if memory_match:
                self.last_memory_usage = int(memory_match.group(1))
            
            # Parse output as JSON
            output_lines = stdout.strip().split('\n')
            if output_lines:
                try:
                    return json.loads(output_lines[0])
                except json.JSONDecodeError:
                    return output_lines[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Subprocess execution error: {str(e)}")
            return str(e)
    
    def analyze_quality(self, code: str) -> Dict[str, float]:
        """
        Analyze JavaScript code quality.
        
        Args:
            code: JavaScript source code
            
        Returns:
            Code quality metrics
        """
        # In a real implementation, this would use tools like ESLint, JSHint, etc.
        # For this example, we'll use simple heuristics
        
        # Count lines of code
        lines = code.strip().split('\n')
        loc = len([line for line in lines if line.strip() and not line.strip().startswith('//')])
        
        # Check for comments
        comment_lines = len([line for line in lines if line.strip().startswith('//')])
        comment_ratio = comment_lines / max(1, loc)
        
        # Check for JSDoc comments
        jsdoc_count = len(re.findall(r'/\*\*.*?\*/', code, re.DOTALL))
        has_jsdoc = jsdoc_count > 0
        
        # Check for function length
        function_bodies = re.findall(r'function\s+\w*\s*\(.*?\)\s*{(.*?)}', code, re.DOTALL)
        function_bodies += re.findall(r'=>\s*{(.*?)}', code, re.DOTALL)
        avg_function_length = sum(len(body.strip().split('\n')) for body in function_bodies) / max(1, len(function_bodies))
        
        # Check for complexity indicators
        complexity_indicators = ['for', 'while', 'if', 'else', 'switch', 'case', 'try', 'catch', '?', '&&', '||']
        complexity_count = sum(len(re.findall(r'\b' + indicator + r'\b', code)) for indicator in complexity_indicators)
        complexity_ratio = complexity_count / max(1, loc)
        
        # Calculate metrics
        complexity = min(1.0, complexity_ratio * 2)  # Higher is more complex
        maintainability = min(1.0, (comment_ratio * 0.5) + (0.3 if has_jsdoc else 0) + (0.2 if avg_function_length < 15 else 0))
        efficiency = max(0.0, 1.0 - (complexity * 0.5))
        best_practices = min(1.0, maintainability * 0.7 + (0.3 if complexity < 0.5 else 0))
        
        # Overall quality score
        overall = (
            (1.0 - complexity) * 0.3 +
            maintainability * 0.3 +
            efficiency * 0.2 +
            best_practices * 0.2
        )
        
        return {
            "complexity": complexity,
            "maintainability": maintainability,
            "efficiency": efficiency,
            "best_practices": best_practices,
            "overall": overall
        }
    
    def get_memory_usage(self) -> int:
        """
        Get memory usage of the last execution.
        
        Returns:
            Memory usage in bytes
        """
        return self.last_memory_usage


class CodingChallengeEvaluator:
    """Evaluates coding challenge solutions."""
    
    def __init__(self, test_cases_repo: Optional[TestCasesRepository] = None):
        """
        Initialize the coding challenge evaluator.
        
        Args:
            test_cases_repo: Repository of test cases
        """
        self.test_cases_repo = test_cases_repo or TestCasesRepository()
        
        # Initialize language analyzers
        self.language_analyzers = {
            "python": PythonAnalyzer(),
            "javascript": JavaScriptAnalyzer()
        }
        
        logger.info(f"Coding challenge evaluator initialized with {len(self.language_analyzers)} language analyzers")
    
    def evaluate_solution(self, challenge_id: str, solution_code: str, language: str) -> Dict[str, Any]:
        """
        Evaluate a coding solution against test cases.
        
        Args:
            challenge_id: Identifier for the coding challenge
            solution_code: Candidate's solution code
            language: Programming language of the solution
            
        Returns:
            Evaluation results
        """
        logger.info(f"Evaluating {language} solution for challenge {challenge_id}")
        
        # Get test cases for this challenge
        test_cases = self.test_cases_repo.get_test_cases(challenge_id)
        
        if not test_cases:
            logger.warning(f"No test cases found for challenge {challenge_id}")
            return {
                "challenge_id": challenge_id,
                "language": language,
                "error": "No test cases found for this challenge",
                "pass_rate": 0,
                "overall_score": 0
            }
        
        # Get language-specific analyzer
        if language not in self.language_analyzers:
            logger.warning(f"Unsupported language: {language}")
            return {
                "challenge_id": challenge_id,
                "language": language,
                "error": f"Unsupported language: {language}",
                "pass_rate": 0,
                "overall_score": 0
            }
        
        analyzer = self.language_analyzers[language]
        
        # Run code against test cases
        test_results = []
        for i, test_case in enumerate(test_cases):
            result = self._run_test_case(solution_code, test_case, analyzer)
            test_results.append({
                "test_case_id": i + 1,
                "input": test_case["input"],
                "expected_output": test_case["expected_output"],
                "actual_output": result["output"],
                "passed": result["passed"],
                "execution_time": result["execution_time"],
                "memory_usage": result["memory_usage"]
            })
        
        # Calculate pass rate
        passed_tests = sum(1 for result in test_results if result["passed"])
        pass_rate = passed_tests / len(test_results) if test_results else 0
        
        # Analyze code quality
        code_quality = analyzer.analyze_quality(solution_code)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(pass_rate, code_quality)
        
        return {
            "challenge_id": challenge_id,
            "language": language,
            "test_results": test_results,
            "pass_rate": pass_rate,
            "code_quality": code_quality,
            "overall_score": overall_score,
            "feedback": self._generate_feedback(test_results, code_quality)
        }
    
    def _run_test_case(self, code: str, test_case: Dict[str, Any], analyzer: LanguageAnalyzer) -> Dict[str, Any]:
        """
        Run a single test case against the solution code.
        
        Args:
            code: Solution code
            test_case: Test case data
            analyzer: Language analyzer
            
        Returns:
            Test result
        """
        try:
            start_time = time.time()
            output = analyzer.execute(code, test_case["input"])
            execution_time = time.time() - start_time
            
            # Check if output matches expected output
            passed = self._compare_outputs(output, test_case["expected_output"])
            
            return {
                "output": output,
                "passed": passed,
                "execution_time": execution_time,
                "memory_usage": analyzer.get_memory_usage()
            }
        except Exception as e:
            logger.error(f"Error running test case: {str(e)}")
            return {
                "output": str(e),
                "passed": False,
                "execution_time": 0,
                "memory_usage": 0
            }
    
    def _compare_outputs(self, actual: Any, expected: Any) -> bool:
        """
        Compare actual output with expected output.
        
        Args:
            actual: Actual output
            expected: Expected output
            
        Returns:
            True if outputs match
        """
        # Handle None values
        if expected is None:
            return actual is None
        
        # Handle different output formats
        if isinstance(expected, (list, dict)):
            # Convert strings to JSON if needed
            if isinstance(actual, str):
                try:
                    actual = json.loads(actual)
                except:
                    return False
            
            # Compare JSON structures
            return self._deep_compare(actual, expected)
        else:
            # Normalize strings
            actual_str = str(actual).strip()
            expected_str = str(expected).strip()
            return actual_str == expected_str
    
    def _deep_compare(self, actual: Any, expected: Any) -> bool:
        """
        Deep comparison of complex data structures.
        
        Args:
            actual: Actual value
            expected: Expected value
            
        Returns:
            True if values match
        """
        # Handle different types
        if type(actual) != type(expected):
            return False
        
        # Handle lists
        if isinstance(expected, list):
            if len(actual) != len(expected):
                return False
            
            return all(self._deep_compare(a, e) for a, e in zip(actual, expected))
        
        # Handle dictionaries
        elif isinstance(expected, dict):
            if set(actual.keys()) != set(expected.keys()):
                return False
            
            return all(self._deep_compare(actual[k], expected[k]) for k in expected)
        
        # Handle primitive types
        else:
            return actual == expected
    
    def _calculate_overall_score(self, pass_rate: float, code_quality: Dict[str, float]) -> float:
        """
        Calculate overall score based on pass rate and code quality.
        
        Args:
            pass_rate: Test case pass rate
            code_quality: Code quality metrics
            
        Returns:
            Overall score (0-100)
        """
        # Weighted average
        weights = {
            "pass_rate": 0.7,
            "code_quality": 0.3
        }
        
        return (
            pass_rate * weights["pass_rate"] +
            code_quality["overall"] * weights["code_quality"]
        ) * 100  # Scale to 0-100
    
    def _generate_feedback(self, test_results: List[Dict[str, Any]], code_quality: Dict[str, float]) -> str:
        """
        Generate feedback based on test results and code quality.
        
        Args:
            test_results: Test case results
            code_quality: Code quality metrics
            
        Returns:
            Feedback text
        """
        feedback = []
        
        # Test case feedback
        failed_tests = [result for result in test_results if not result["passed"]]
        if failed_tests:
            feedback.append(f"Failed {len(failed_tests)} out of {len(test_results)} test cases.")
            
            # Add details for first few failed tests
            for i, test in enumerate(failed_tests[:3]):
                feedback.append(f"Test case {test['test_case_id']}: Expected '{test['expected_output']}', got '{test['actual_output']}'")
        else:
            feedback.append("All test cases passed successfully!")
        
        # Code quality feedback
        if code_quality["overall"] < 0.5:
            feedback.append("Code quality needs improvement:")
            if code_quality["complexity"] > 0.7:
                feedback.append("- High complexity. Consider simplifying your solution.")
            if code_quality["maintainability"] < 0.5:
                feedback.append("- Low maintainability. Add comments and improve variable naming.")
            if code_quality["efficiency"] < 0.5:
                feedback.append("- Efficiency could be improved. Check for unnecessary operations.")
        else:
            feedback.append("Good code quality overall.")
            if code_quality["best_practices"] > 0.8:
                feedback.append("- Excellent adherence to best practices!")
        
        return "\n".join(feedback)


class TechnicalAssessmentEvaluator:
    """Evaluates technical assessments beyond coding challenges."""
    
    def __init__(self):
        """Initialize the technical assessment evaluator."""
        logger.info("Technical assessment evaluator initialized")
    
    def evaluate_assessment(self, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a technical assessment.
        
        Args:
            assessment_data: Assessment data including questions and answers
            
        Returns:
            Evaluation results
        """
        logger.info(f"Evaluating technical assessment with {len(assessment_data.get('questions', []))} questions")
        
        # Extract questions and answers
        questions = assessment_data.get("questions", [])
        
        # Evaluate each question
        question_evaluations = []
        for question in questions:
            question_id = question.get("id", "unknown")
            question_type = question.get("type", "unknown")
            question_text = question.get("text", "")
            answer = question.get("answer", "")
            expected_answer = question.get("expected_answer", "")
            
            # Evaluate based on question type
            if question_type == "multiple_choice":
                evaluation = self._evaluate_multiple_choice(question, answer)
            elif question_type == "true_false":
                evaluation = self._evaluate_true_false(question, answer)
            elif question_type == "short_answer":
                evaluation = self._evaluate_short_answer(question, answer)
            else:
                logger.warning(f"Unknown question type: {question_type}")
                evaluation = {
                    "score": 0,
                    "feedback": f"Unknown question type: {question_type}"
                }
            
            question_evaluations.append({
                "question_id": question_id,
                "question_type": question_type,
                "question_text": question_text,
                "answer": answer,
                "expected_answer": expected_answer,
                "score": evaluation["score"],
                "feedback": evaluation["feedback"]
            })
        
        # Calculate overall score
        if question_evaluations:
            overall_score = sum(q["score"] for q in question_evaluations) / len(question_evaluations) * 100
        else:
            overall_score = 0
        
        # Identify strengths and weaknesses
        strengths, weaknesses = self._identify_strengths_weaknesses(question_evaluations)
        
        return {
            "assessment_id": assessment_data.get("id", "unknown"),
            "candidate_id": assessment_data.get("candidate_id", "unknown"),
            "job_id": assessment_data.get("job_id", "unknown"),
            "question_evaluations": question_evaluations,
            "overall_score": overall_score,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "feedback": self._generate_overall_feedback(question_evaluations, overall_score)
        }
    
    def _evaluate_multiple_choice(self, question: Dict[str, Any], answer: Any) -> Dict[str, Any]:
        """
        Evaluate a multiple choice question.
        
        Args:
            question: Question data
            answer: Candidate's answer
            
        Returns:
            Evaluation result
        """
        correct_answer = question.get("correct_answer")
        
        if answer == correct_answer:
            return {
                "score": 1.0,
                "feedback": "Correct answer!"
            }
        else:
            return {
                "score": 0.0,
                "feedback": f"Incorrect. The correct answer is: {correct_answer}"
            }
    
    def _evaluate_true_false(self, question: Dict[str, Any], answer: Any) -> Dict[str, Any]:
        """
        Evaluate a true/false question.
        
        Args:
            question: Question data
            answer: Candidate's answer
            
        Returns:
            Evaluation result
        """
        correct_answer = question.get("correct_answer")
        
        if answer == correct_answer:
            return {
                "score": 1.0,
                "feedback": "Correct answer!"
            }
        else:
            return {
                "score": 0.0,
                "feedback": f"Incorrect. The correct answer is: {correct_answer}"
            }
    
    def _evaluate_short_answer(self, question: Dict[str, Any], answer: str) -> Dict[str, Any]:
        """
        Evaluate a short answer question.
        
        Args:
            question: Question data
            answer: Candidate's answer
            
        Returns:
            Evaluation result
        """
        keywords = question.get("keywords", [])
        
        if not keywords:
            logger.warning("No keywords defined for short answer question")
            return {
                "score": 0.5,  # Neutral score
                "feedback": "Unable to evaluate answer automatically"
            }
        
        # Count keywords in answer
        answer_lower = answer.lower()
        found_keywords = [keyword for keyword in keywords if keyword.lower() in answer_lower]
        
        # Calculate score based on keyword coverage
        score = len(found_keywords) / len(keywords)
        
        # Generate feedback
        if score >= 0.8:
            feedback = "Excellent answer covering all key points!"
        elif score >= 0.6:
            feedback = "Good answer covering most key points."
        elif score >= 0.4:
            feedback = "Adequate answer but missing some key points."
        else:
            feedback = "Answer is missing many key points."
            
        # Add missing keywords
        missing_keywords = [keyword for keyword in keywords if keyword.lower() not in answer_lower]
        if missing_keywords:
            feedback += f" Consider including: {', '.join(missing_keywords)}"
        
        return {
            "score": score,
            "feedback": feedback
        }
    
    def _identify_strengths_weaknesses(self, question_evaluations: List[Dict[str, Any]]) -> tuple:
        """
        Identify strengths and weaknesses based on question evaluations.
        
        Args:
            question_evaluations: List of question evaluations
            
        Returns:
            Tuple of (strengths, weaknesses)
        """
        if not question_evaluations:
            return [], []
        
        # Group questions by category
        questions_by_category = {}
        for q in question_evaluations:
            category = q.get("category", "general")
            if category not in questions_by_category:
                questions_by_category[category] = []
            questions_by_category[category].append(q)
        
        # Calculate category scores
        category_scores = {}
        for category, questions in questions_by_category.items():
            category_scores[category] = sum(q["score"] for q in questions) / len(questions)
        
        # Identify strengths (categories with high scores)
        strengths = [
            f"Strong knowledge in {category}" 
            for category, score in category_scores.items() 
            if score >= 0.8
        ]
        
        # Identify weaknesses (categories with low scores)
        weaknesses = [
            f"Knowledge gap in {category}" 
            for category, score in category_scores.items() 
            if score <= 0.4
        ]
        
        return strengths, weaknesses
    
    def _generate_overall_feedback(self, question_evaluations: List[Dict[str, Any]], overall_score: float) -> str:
        """
        Generate overall feedback based on question evaluations.
        
        Args:
            question_evaluations: List of question evaluations
            overall_score: Overall assessment score
            
        Returns:
            Overall feedback
        """
        if not question_evaluations:
            return "No questions were evaluated."
        
        # Count correct and incorrect answers
        correct_count = sum(1 for q in question_evaluations if q["score"] >= 0.8)
        incorrect_count = sum(1 for q in question_evaluations if q["score"] <= 0.2)
        
        # Generate feedback based on overall score
        if overall_score >= 90:
            feedback = "Excellent technical knowledge demonstrated across all areas."
        elif overall_score >= 80:
            feedback = "Strong technical knowledge with minor gaps in some areas."
        elif overall_score >= 70:
            feedback = "Good technical knowledge but with some notable gaps."
        elif overall_score >= 60:
            feedback = "Adequate technical knowledge but significant improvement needed in some areas."
        else:
            feedback = "Technical knowledge below expectations for this role."
        
        # Add details about correct/incorrect answers
        feedback += f" Correctly answered {correct_count} out of {len(question_evaluations)} questions."
        
        return feedback


# Example usage
if __name__ == "__main__":
    # Example coding challenge solution
    challenge_id = "reverse_string"
    python_solution = """
def reverse_string(s):
    return s[::-1]
"""
    
    javascript_solution = """
function reverseString(s) {
    return s.split('').reverse().join('');
}
"""
    
    # Initialize evaluator
    test_cases_repo = TestCasesRepository()
    evaluator = CodingChallengeEvaluator(test_cases_repo)
    
    # Evaluate Python solution
    print("Evaluating Python solution:")
    python_result = evaluator.evaluate_solution(challenge_id, python_solution, "python")
    
    print(f"Pass rate: {python_result['pass_rate'] * 100:.1f}%")
    print(f"Code quality: {python_result['code_quality']['overall']:.2f}")
    print(f"Overall score: {python_result['overall_score']:.1f}")
    print(f"Feedback: {python_result['feedback']}")
    
    # Evaluate JavaScript solution
    print("\nEvaluating JavaScript solution:")
    js_result = evaluator.evaluate_solution(challenge_id, javascript_solution, "javascript")
    
    print(f"Pass rate: {js_result['pass_rate'] * 100:.1f}%")
    print(f"Code quality: {js_result['code_quality']['overall']:.2f}")
    print(f"Overall score: {js_result['overall_score']:.1f}")
    print(f"Feedback: {js_result['feedback']}")
    
    # Example technical assessment
    assessment_data = {
        "id": "assessment_12345",
        "candidate_id": "candidate_67890",
        "job_id": "job_54321",
        "questions": [
            {
                "id": "q1",
                "type": "multiple_choice",
                "text": "Which data structure would be most efficient for implementing a priority queue?",
                "options": ["Array", "Linked List", "Heap", "Hash Table"],
                "correct_answer": "Heap",
                "answer": "Heap",
                "category": "data_structures"
            },
            {
                "id": "q2",
                "type": "true_false",
                "text": "HTTP is a stateless protocol.",
                "correct_answer": True,
                "answer": True,
                "category": "networking"
            },
            {
                "id": "q3",
                "type": "short_answer",
                "text": "Explain the concept of database normalization.",
                "keywords": ["redundancy", "anomalies", "normal forms", "dependencies", "relations"],
                "answer": "Database normalization is the process of structuring a database to reduce redundancy and improve data integrity. It involves organizing fields and tables to minimize duplication and avoid update anomalies.",
                "category": "databases"
            }
        ]
    }
    
    # Initialize technical assessment evaluator
    tech_evaluator = TechnicalAssessmentEvaluator()
    
    # Evaluate assessment
    print("\nEvaluating technical assessment:")
    assessment_result = tech_evaluator.evaluate_assessment(assessment_data)
    
    print(f"Overall score: {assessment_result['overall_score']:.1f}")
    print("Question evaluations:")
    for q in assessment_result['question_evaluations']:
        print(f"- {q['question_text']}: {q['score']:.1f}")
        print(f"  Feedback: {q['feedback']}")
    
    print(f"Overall feedback: {assessment_result['feedback']}")
