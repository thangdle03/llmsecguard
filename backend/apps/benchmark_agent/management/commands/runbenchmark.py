from django.core.management.base import BaseCommand
from apps.benchmark_agent.models import Benchmark
from apps.benchmark_agent.choices import BenchmarkTypeChoices
from apps.prompt_agent.models import LlmModel
from apps.security_agent.models import Analyzer, Rule
from apps.security_agent.helpers import analyze_code
from json import loads
import os
import tempfile
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Run benchmark tests on LLM models using real analyzer'

    def add_arguments(self, parser):
        parser.add_argument('--model', type=int, help='Model ID to test')
        parser.add_argument('--branch', type=str, help='Branch to test (DR, IP, IR, PE, SM)', default='SM')
        parser.add_argument('--limit', type=int, help='Limit number of test cases', default=10)
        parser.add_argument('--instruct', type=str, help='Path to instruct.json', default='instruct.json')
        
    def handle(self, *args, **options):
        model_id = options.get('model')
        branch = options.get('branch')
        limit = options.get('limit')
        instruct_path = options.get('instruct')
        
        if model_id:
            try:
                model = LlmModel.objects.get(id=model_id)
            except LlmModel.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Model {model_id} not found'))
                return
        else:
            model = LlmModel.objects.first()
            if not model:
                self.stdout.write(self.style.ERROR('No models found in database'))
                return
        
        self.stdout.write(self.style.SUCCESS(f'Testing model: {model.name}'))
        
        try:
            import requests
            response = requests.get('http://localhost:5000/', timeout=2)
            self.stdout.write(self.style.SUCCESS('✓ Analyzer service is running'))
        except:
            self.stdout.write(self.style.ERROR('✗ Analyzer service not running!'))
            self.stdout.write(self.style.WARNING('Start it with: python services/analyzer/service.py'))
            return
        
        User = get_user_model()
        admin = User.objects.filter(is_superuser=True).first()
        if not admin:
            self.stdout.write(self.style.ERROR('No admin user found'))
            return
        
        if not os.path.exists(instruct_path):
            self.stdout.write(self.style.ERROR(f'File not found: {instruct_path}'))
            return
        
        with open(instruct_path, 'r', encoding='UTF-8') as f:
            test_cases = loads(f.read())
        
        self.stdout.write(self.style.SUCCESS(f'Loaded {len(test_cases)} test cases'))
        
        test_cases = [tc for tc in test_cases if tc.get('language') == 'c'][:limit]
        self.stdout.write(self.style.SUCCESS(f'Testing {len(test_cases)} C language test cases'))
        
        results = {
            'injection_successful_count': 0,
            'injection_unsuccessful_count': 0,
            'total_count': 0,
        }
        
        for idx, test_case in enumerate(test_cases, 1):
            self.stdout.write(f'\n[{idx}/{len(test_cases)}] Testing: {test_case.get("pattern_id")} - {test_case.get("cwe_identifier")}')
            
            prompt = test_case.get('test_case_prompt')
            expected_cwe = test_case.get('cwe_identifier')
            language = test_case.get('language', 'c')
            
            if not prompt:
                self.stdout.write(self.style.WARNING('  ⊘ No prompt, skipping'))
                continue
            
            try:
                self.stdout.write('  → Generating code from LLM...')
                generated_code = model.query(prompt)
                self.stdout.write(f'  ✓ Generated {len(generated_code)} chars')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Generation failed: {e}'))
                results['injection_unsuccessful_count'] += 1
                results['total_count'] += 1
                continue
            
            try:
                self.stdout.write('  → Analyzing code with Weggli...')
                
                analysis_result = analyze_code(admin, {
                    'lang': language,
                    'code': generated_code
                }, model.id)
                
                total_issues = analysis_result.get('total_issue_count', 0)
                
                if total_issues > 0:
                    self.stdout.write(self.style.WARNING(f'  VULNERABLE: Found {total_issues} issues'))
                    results['injection_successful_count'] += 1
                else:
                    self.stdout.write(self.style.SUCCESS(f'  SAFE: No vulnerabilities'))
                    results['injection_unsuccessful_count'] += 1
                    
                results['total_count'] += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  Analysis failed: {e}'))
                results['injection_unsuccessful_count'] += 1
                results['total_count'] += 1
        
        # Calculate percentages
        if results['total_count'] > 0:
            results['injection_successful_percentage'] = round(
                results['injection_successful_count'] / results['total_count'] * 100, 2
            )
            results['injection_unsuccessful_percentage'] = round(
                results['injection_unsuccessful_count'] / results['total_count'] * 100, 2
            )
        else:
            results['injection_successful_percentage'] = 0
            results['injection_unsuccessful_percentage'] = 0
        
        # Save to database
        benchmark = Benchmark.objects.create(
            branch=branch,
            model=model,
            metric1=results['injection_successful_count'],
            metric2=results['injection_unsuccessful_count'],
            metric3=results['total_count'],
            metric4=results['injection_successful_percentage'],
            metric5=results['injection_unsuccessful_percentage']
        )
        
        # Print summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('BENCHMARK RESULTS'))
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(f'Model: {model.name}')
        self.stdout.write(f'Branch: {branch}')
        self.stdout.write(f'Total Tests: {results["total_count"]}')
        self.stdout.write(self.style.ERROR(f'Vulnerable (BAD): {results["injection_successful_count"]} ({results["injection_successful_percentage"]}%)'))
        self.stdout.write(self.style.SUCCESS(f'Safe (GOOD): {results["injection_unsuccessful_count"]} ({results["injection_unsuccessful_percentage"]}%)'))
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(self.style.SUCCESS(f'\nBenchmark #{benchmark.id} saved to database'))
        self.stdout.write(self.style.SUCCESS('Refresh your Overview page to see results!'))