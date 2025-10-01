"""
Scenario Engine: Sensitivity analysis and what-if modeling
"""

from typing import Dict, Callable, Any, List, Tuple
import copy


def calculate_sensitivity(
    baseline_fn: Callable[[Dict], float],
    inputs: Dict[str, float],
    bump_pct: float = 0.01,
    metric_name: str = "output"
) -> Dict[str, Dict[str, float]]:
    """
    Calculate sensitivity of output to each input variable.
    
    Args:
        baseline_fn: Function that takes inputs dict and returns a single metric
        inputs: Dictionary of input variables {name: value}
        bump_pct: How much to bump each input (0.01 = 1%)
        metric_name: Name of the output metric for display
    
    Returns:
        Dict mapping input name to sensitivity metrics:
        {
            'close_rate': {
                'baseline': 0.30,
                'bumped': 0.303,
                'output_baseline': 100000,
                'output_bumped': 101000,
                'sensitivity': 0.01,  # 1% change in output per 1% change in input
                'rank': 1
            },
            ...
        }
    """
    baseline_output = baseline_fn(inputs)
    sensitivities = {}
    
    for key, value in inputs.items():
        if value == 0:
            # Can't bump zero values meaningfully
            sensitivities[key] = {
                'baseline': value,
                'bumped': value,
                'output_baseline': baseline_output,
                'output_bumped': baseline_output,
                'sensitivity': 0,
                'abs_sensitivity': 0
            }
            continue
        
        # Create bumped inputs
        bumped_inputs = inputs.copy()
        bumped_inputs[key] = value * (1 + bump_pct)
        
        # Calculate new output
        bumped_output = baseline_fn(bumped_inputs)
        
        # Calculate sensitivity (% change in output / % change in input)
        if baseline_output != 0:
            output_change_pct = (bumped_output - baseline_output) / baseline_output
            sensitivity = output_change_pct / bump_pct  # Normalize to 1% input change
        else:
            sensitivity = 0
        
        sensitivities[key] = {
            'baseline': value,
            'bumped': bumped_inputs[key],
            'output_baseline': baseline_output,
            'output_bumped': bumped_output,
            'sensitivity': sensitivity,
            'abs_sensitivity': abs(sensitivity),  # For ranking
            'abs_change': abs(bumped_output - baseline_output)
        }
    
    # Rank by absolute sensitivity
    sorted_items = sorted(
        sensitivities.items(),
        key=lambda x: x[1]['abs_sensitivity'],
        reverse=True
    )
    
    for rank, (key, data) in enumerate(sorted_items, 1):
        sensitivities[key]['rank'] = rank
    
    return sensitivities


def multi_metric_sensitivity(
    baseline_fn: Callable[[Dict], Dict[str, float]],
    inputs: Dict[str, float],
    bump_pct: float = 0.01
) -> Dict[str, Dict[str, Any]]:
    """
    Calculate sensitivity for multiple output metrics at once.
    
    Args:
        baseline_fn: Function returning dict of metrics {metric_name: value}
        inputs: Input variables
        bump_pct: Bump percentage
    
    Returns:
        Nested dict: {metric_name: {input_name: sensitivity_data}}
    """
    baseline_outputs = baseline_fn(inputs)
    results = {metric: {} for metric in baseline_outputs.keys()}
    
    for key, value in inputs.items():
        if value == 0:
            for metric in baseline_outputs.keys():
                results[metric][key] = {
                    'sensitivity': 0,
                    'abs_sensitivity': 0,
                    'abs_change': 0
                }
            continue
        
        # Bump this input
        bumped_inputs = inputs.copy()
        bumped_inputs[key] = value * (1 + bump_pct)
        bumped_outputs = baseline_fn(bumped_inputs)
        
        # Calculate sensitivity for each metric
        for metric, baseline_val in baseline_outputs.items():
            bumped_val = bumped_outputs[metric]
            
            if baseline_val != 0:
                output_change_pct = (bumped_val - baseline_val) / baseline_val
                sensitivity = output_change_pct / bump_pct
            else:
                sensitivity = 0
            
            results[metric][key] = {
                'baseline': baseline_val,
                'bumped': bumped_val,
                'sensitivity': sensitivity,
                'abs_sensitivity': abs(sensitivity),
                'abs_change': abs(bumped_val - baseline_val)
            }
    
    # Rank each metric's sensitivities
    for metric, sensitivities in results.items():
        sorted_items = sorted(
            sensitivities.items(),
            key=lambda x: x[1]['abs_sensitivity'],
            reverse=True
        )
        for rank, (key, data) in enumerate(sorted_items, 1):
            results[metric][key]['rank'] = rank
    
    return results


def get_top_drivers(
    sensitivities: Dict[str, Dict[str, Any]],
    metric: str,
    top_n: int = 5
) -> List[Tuple[str, float]]:
    """
    Get top N drivers for a specific metric.
    
    Returns:
        List of (input_name, sensitivity) sorted by absolute sensitivity
    """
    if metric not in sensitivities:
        return []
    
    items = [
        (key, data['sensitivity'])
        for key, data in sensitivities[metric].items()
    ]
    
    sorted_items = sorted(items, key=lambda x: abs(x[1]), reverse=True)
    return sorted_items[:top_n]


def create_scenario_delta(
    baseline_inputs: Dict[str, float],
    changes: Dict[str, float]
) -> Dict[str, float]:
    """
    Create a scenario by applying absolute changes to baseline.
    
    Args:
        baseline_inputs: Current state
        changes: Absolute changes {key: +/-value}
    
    Returns:
        New inputs dict with changes applied
    """
    scenario = baseline_inputs.copy()
    for key, change in changes.items():
        if key in scenario:
            scenario[key] = scenario[key] + change
    return scenario


def compare_scenarios(
    scenario_a: Dict[str, float],
    scenario_b: Dict[str, float],
    calculator_fn: Callable[[Dict], Dict[str, float]]
) -> Dict[str, Dict[str, float]]:
    """
    Compare two scenarios side by side.
    
    Returns:
        {
            'scenario_a': {metric: value},
            'scenario_b': {metric: value},
            'delta': {metric: diff},
            'delta_pct': {metric: % change}
        }
    """
    results_a = calculator_fn(scenario_a)
    results_b = calculator_fn(scenario_b)
    
    delta = {}
    delta_pct = {}
    
    for metric in results_a.keys():
        diff = results_b[metric] - results_a[metric]
        delta[metric] = diff
        
        if results_a[metric] != 0:
            delta_pct[metric] = (diff / results_a[metric]) * 100
        else:
            delta_pct[metric] = 0 if diff == 0 else float('inf')
    
    return {
        'scenario_a': results_a,
        'scenario_b': results_b,
        'delta': delta,
        'delta_pct': delta_pct
    }


class ScenarioManager:
    """
    Manage named scenarios for comparison.
    """
    
    def __init__(self):
        self.scenarios: Dict[str, Dict[str, float]] = {}
        self.descriptions: Dict[str, str] = {}
    
    def add_scenario(self, name: str, inputs: Dict[str, float], description: str = ""):
        """Save a named scenario"""
        self.scenarios[name] = copy.deepcopy(inputs)
        self.descriptions[name] = description
    
    def get_scenario(self, name: str) -> Dict[str, float]:
        """Retrieve a scenario by name"""
        return copy.deepcopy(self.scenarios.get(name, {}))
    
    def list_scenarios(self) -> List[str]:
        """List all scenario names"""
        return list(self.scenarios.keys())
    
    def compare(
        self,
        name_a: str,
        name_b: str,
        calculator_fn: Callable[[Dict], Dict[str, float]]
    ) -> Dict:
        """Compare two saved scenarios"""
        scenario_a = self.get_scenario(name_a)
        scenario_b = self.get_scenario(name_b)
        
        if not scenario_a or not scenario_b:
            raise ValueError(f"Scenario not found")
        
        return compare_scenarios(scenario_a, scenario_b, calculator_fn)
    
    def delete_scenario(self, name: str):
        """Delete a scenario"""
        if name in self.scenarios:
            del self.scenarios[name]
        if name in self.descriptions:
            del self.descriptions[name]
    
    def export_to_dict(self) -> Dict:
        """Export all scenarios to a dict (for JSON serialization)"""
        return {
            'scenarios': self.scenarios,
            'descriptions': self.descriptions
        }
    
    def import_from_dict(self, data: Dict):
        """Import scenarios from a dict"""
        self.scenarios = copy.deepcopy(data.get('scenarios', {}))
        self.descriptions = copy.deepcopy(data.get('descriptions', {}))
