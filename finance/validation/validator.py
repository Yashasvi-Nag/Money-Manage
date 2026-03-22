class ValidationEngine:
    def validate(self, stated_total, computed_total, tolerance=1.0):
        diff = computed_total - stated_total
        is_valid = abs(diff) <= tolerance
        return (is_valid, diff)
