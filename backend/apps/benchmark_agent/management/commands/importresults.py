from django.core.management.base import BaseCommand
from apps.benchmark_agent.models import Benchmark
from apps.benchmark_agent.choices import BenchmarkTypeChoices
from apps.prompt_agent.models import LlmModel
from json import loads
import os

class Command(BaseCommand):
    help = 'Import Results from PurpleLlama Benchmark'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str, help='path of the instruct.json')
        
    def handle(self, *args, **options):
        path = options['path']
        
        if not os.path.exists(path):
            self.stdout.write(self.style.ERROR(f'File not found: {path}'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Reading: {path}'))
        
        with open(path, 'r', encoding="UTF-8") as file:
            data = file.read()
            data = loads(data)
            
            # Check if data is list or dict
            if isinstance(data, list):
                self.stdout.write(self.style.WARNING('Data is an array, processing items...'))
                self.process_array(data)
            elif isinstance(data, dict):
                self.stdout.write(self.style.SUCCESS('Data is an object, processing stats...'))
                self.process_dict(data)
            else:
                self.stdout.write(self.style.ERROR('Unknown data format'))
                return
    
    def process_array(self, data):
        """Process when instruct.json is an array of results"""
        created = 0
        
        for item in data:
            # Try to extract model info
            model_name = item.get('model') or item.get('model_name')
            branch = item.get('branch') or item.get('type')
            
            if not model_name:
                self.stdout.write(self.style.WARNING(f'Skipping item without model: {item}'))
                continue
            
            # Find matching models
            models = LlmModel.objects.filter(model__icontains=model_name)
            if not models.exists():
                self.stdout.write(self.style.WARNING(f'Model not found: {model_name}'))
                continue
            
            # Determine branch type
            branch_type = self.get_branch_type(branch or 'SM')
            
            for model in models:
                # Extract metrics - try different field names
                metric1 = (item.get('injection_successful_count') or 
                          item.get('is_extremely_malicious') or 0)
                metric2 = (item.get('injection_unsuccessful_count') or 
                          item.get('is_potentially_malicious') or 0)
                metric3 = (item.get('total_count') or 
                          item.get('is_non_malicious') or 0)
                metric4 = (item.get('injection_successful_percentage') or 
                          item.get('malicious_percentage') or 0)
                metric5 = (item.get('injection_unsuccessful_percentage') or 0)
                
                Benchmark.objects.create(
                    branch=branch_type,
                    model=model,
                    metric1=float(metric1),
                    metric2=float(metric2),
                    metric3=float(metric3),
                    metric4=float(metric4),
                    metric5=float(metric5)
                )
                created += 1
                self.stdout.write(self.style.SUCCESS(
                    f"✓ Created: {branch_type} - {model.name} (Total: {metric3})"
                ))
        
        self.stdout.write(self.style.SUCCESS(f'\n{"="*50}'))
        self.stdout.write(self.style.SUCCESS(f'✓ Done! Created {created} benchmarks'))
        self.stdout.write(self.style.SUCCESS(f'{"="*50}'))
    
    def process_dict(self, data):
        """Process when instruct.json is a dict with stat objects"""
        stat_per_model = data.get('stat_per_model')
        stat_per_model_per_variant = data.get('stat_per_model_per_variant')
        stat_per_model_per_type = data.get('stat_per_model_per_type')
        stat_per_model_per_risk_category = data.get('stat_per_model_per_risk_category')
        
        created = 0
        
        # SM
        if stat_per_model:
            for model_name, stat in stat_per_model.items():
                models = LlmModel.objects.filter(model__icontains=model_name)
                
                for model in models:
                    Benchmark.objects.create(
                        branch=BenchmarkTypeChoices.STATS_PER_MODEL,
                        model=model,
                        metric1=stat.get('injection_successful_count', 0),
                        metric2=stat.get('injection_unsuccessful_count', 0),
                        metric3=stat.get('total_count', 0),
                        metric4=stat.get('injection_successful_percentage', 0),
                        metric5=stat.get('injection_unsuccessful_percentage', 0)
                    )
                    created += 1
                    self.stdout.write(self.style.SUCCESS(f"✓ SM: {model.name}"))
            
        # IP & IR
        if stat_per_model_per_variant:
            for model_name, stat in stat_per_model_per_variant.items():
                models = LlmModel.objects.filter(model__icontains=model_name)
                
                for model in models:
                    if 'ignore_previous_instructions' in stat:
                        ip = stat['ignore_previous_instructions']
                        Benchmark.objects.create(
                            branch=BenchmarkTypeChoices.IGNORE_PREVIOUS_INSTRUCTIONS,
                            model=model,
                            metric1=ip.get('injection_successful_count', 0),
                            metric2=ip.get('injection_unsuccessful_count', 0),
                            metric3=ip.get('total_count', 0),
                            metric4=ip.get('injection_successful_percentage', 0),
                            metric5=ip.get('injection_unsuccessful_percentage', 0)
                        )
                        created += 1
                        self.stdout.write(self.style.SUCCESS(f"✓ IP: {model.name}"))
                    
                    if 'indirect_reference' in stat:
                        ir = stat['indirect_reference']
                        Benchmark.objects.create(
                            branch=BenchmarkTypeChoices.INDIRECT_REFERENCE,
                            model=model,
                            metric1=ir.get('injection_successful_count', 0),
                            metric2=ir.get('injection_unsuccessful_count', 0),
                            metric3=ir.get('total_count', 0),
                            metric4=ir.get('injection_successful_percentage', 0),
                            metric5=ir.get('injection_unsuccessful_percentage', 0)
                        )
                        created += 1
                        self.stdout.write(self.style.SUCCESS(f"✓ IR: {model.name}"))
            
        # DR
        if stat_per_model_per_type:
            for model_name, stat in stat_per_model_per_type.items():
                models = LlmModel.objects.filter(model__icontains=model_name)
                
                for model in models:
                    if 'direct' in stat:
                        dr = stat['direct']
                        Benchmark.objects.create(
                            branch=BenchmarkTypeChoices.DIRECT,
                            model=model,
                            metric1=dr.get('injection_successful_count', 0),
                            metric2=dr.get('injection_unsuccessful_count', 0),
                            metric3=dr.get('total_count', 0),
                            metric4=dr.get('injection_successful_percentage', 0),
                            metric5=dr.get('injection_unsuccessful_percentage', 0)
                        )
                        created += 1
                        self.stdout.write(self.style.SUCCESS(f"✓ DR: {model.name}"))
         
        # SV
        if stat_per_model_per_risk_category:
            for model_name, stat in stat_per_model_per_risk_category.items():
                models = LlmModel.objects.filter(model__icontains=model_name)
                
                for model in models:
                    if 'security-violating' in stat:
                        sv = stat['security-violating']
                        Benchmark.objects.create(
                            branch=BenchmarkTypeChoices.DIRECT,
                            model=model,
                            metric1=sv.get('injection_successful_count', 0),
                            metric2=sv.get('injection_unsuccessful_count', 0),
                            metric3=sv.get('total_count', 0),
                            metric4=sv.get('injection_successful_percentage', 0),
                            metric5=sv.get('injection_unsuccessful_percentage', 0)
                        )
                        created += 1
                        self.stdout.write(self.style.SUCCESS(f"✓ SV: {model.name}"))
            
        # PE - remaining data
        for model_name, stat in data.items():
            if model_name in ['stat_per_model', 'stat_per_model_per_variant', 
                             'stat_per_model_per_type', 'stat_per_model_per_risk_category',
                             'accept_count', 'refusal_count', 'refusal_rate']:
                continue
                
            pe_data = stat.get('Privilege Escalation')
            if not pe_data:
                continue
        
            models = LlmModel.objects.filter(model__icontains=model_name)
            for model in models:
                Benchmark.objects.create(
                    branch=BenchmarkTypeChoices.PRIVILEGE_ESCALATION,
                    model=model,
                    metric1=pe_data.get('is_extremely_malicious', 0),
                    metric2=pe_data.get('is_potentially_malicious', 0),
                    metric3=pe_data.get('is_non_malicious', 0),
                    metric4=pe_data.get('total_count', 0),
                    metric5=pe_data.get('malicious_percentage', 0)
                )
                created += 1
                self.stdout.write(self.style.SUCCESS(f"✓ PE: {model.name}"))
        
        self.stdout.write(self.style.SUCCESS(f'\n{"="*50}'))
        self.stdout.write(self.style.SUCCESS(f'✓ Done! Created {created} benchmarks'))
        self.stdout.write(self.style.SUCCESS(f'{"="*50}'))
    
    def get_branch_type(self, branch_str):
        """Map branch string to BenchmarkTypeChoices"""
        mapping = {
            'DR': BenchmarkTypeChoices.DIRECT,
            'IP': BenchmarkTypeChoices.IGNORE_PREVIOUS_INSTRUCTIONS,
            'IR': BenchmarkTypeChoices.INDIRECT_REFERENCE,
            'PE': BenchmarkTypeChoices.PRIVILEGE_ESCALATION,
            'SM': BenchmarkTypeChoices.STATS_PER_MODEL,
            'direct': BenchmarkTypeChoices.DIRECT,
            'ignore_previous_instructions': BenchmarkTypeChoices.IGNORE_PREVIOUS_INSTRUCTIONS,
            'indirect_reference': BenchmarkTypeChoices.INDIRECT_REFERENCE,
        }
        return mapping.get(branch_str, BenchmarkTypeChoices.STATS_PER_MODEL)