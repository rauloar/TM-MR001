class BehaviorEngine:

    def __init__(self, session):
        self.session = session

    def get_active_rules(self, fecha_inicio):
        from attendance.models.rule_set import RuleSet

        return self.session.query(RuleSet)\
            .filter(RuleSet.fecha_inicio <= fecha_inicio)\
            .filter(
                (RuleSet.fecha_fin == None) |
                (RuleSet.fecha_fin >= fecha_inicio)
            )\
            .order_by(RuleSet.version.desc())\
            .first()

    def evaluate(self, user_identifier, features, fecha_inicio, fecha_fin):

        rule_set = self.get_active_rules(fecha_inicio)

        if not rule_set:
            return {
                "user_identifier": user_identifier,
                "features": features,
                "score": 0,
                "risk": "SIN_REGLAS"
            }

        score = 0
        triggered = []

        for rule in rule_set.rules:
            metric_value = features.get(rule.metric_name)

            if metric_value is None:
                continue

            if self.compare(metric_value, rule.operator, rule.threshold):
                score += rule.weight
                triggered.append(rule.metric_name)

        risk = self.classify(score)

        return {
            "user_identifier": user_identifier,
            "features": features,
            "score": round(score, 3),
            "risk": risk,
            "triggered_rules": triggered
        }

    def compare(self, value, operator, threshold):
        if operator == ">":
            return value > threshold
        if operator == "<":
            return value < threshold
        if operator == ">=":
            return value >= threshold
        if operator == "<=":
            return value <= threshold
        if operator == "==":
            return value == threshold
        return False

    def classify(self, score):
        if score > 0.7:
            return "ALTO"
        elif score > 0.4:
            return "MEDIO"
        return "BAJO"