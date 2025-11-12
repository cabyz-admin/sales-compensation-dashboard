"""
Test to understand Streamlit number_input behavior with and without value parameter
"""

# Test Case 1: Positional parameters
# st.number_input("Closers", 1, 50, key="num_closers_main")
# Maps to: label="Closers", min_value=1, max_value=50, value=<not provided>
# Expected behavior: Reads from session_state['num_closers_main']
# Fallback: If session_state['num_closers_main'] doesn't exist, uses min_value (1)

# Test Case 2: Positional parameters with step
# st.number_input("Base Salary", 0, 200000, step=1000, key="closer_base")
# Maps to: label="Base Salary", min_value=0, max_value=200000, step=1000, value=<not provided>
# Expected behavior: Reads from session_state['closer_base']
# Fallback: If session_state['closer_base'] doesn't exist, uses min_value (0)

# Test Case 3: Named parameters with explicit value (CORRECT)
# st.number_input("Monthly Premium", min_value=0.0, value=st.session_state.get('calc_monthly_premium', 2000.0), key="calc_monthly_premium")
# Expected behavior: ALWAYS uses the value parameter (which reads from session_state or uses 2000.0 default)
# This is SAFE because value is explicit

# CRITICAL INSIGHT:
# When widgets use POSITIONAL parameters without explicit value:
#   st.number_input(label, min, max, key=X)
#
# Streamlit behavior:
#   1. First render: session_state[X] doesn't exist
#   2. Widget defaults to min_value
#   3. User interacts, sets to Y
#   4. session_state[X] = Y
#   5. Rerun triggered
#   6. Widget SHOULD read session_state[X] and show Y
#
# BUT if there's ANY code that:
#   - Clears session_state[X]
#   - Reinitializes it
#   - Triggers rerun before widget renders
# Then widget falls back to min_value!

# THE BUG:
# The problem is NOT that widgets don't have value parameter
# The problem is that SOMETHING is clearing or reinitializing session_state
# between user interaction and widget render!

# Let me search for what's clearing session state...
