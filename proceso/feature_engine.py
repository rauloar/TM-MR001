from datetime import datetime
from collections import defaultdict
import statistics
import numpy as np


class FeatureEngine:

    def __init__(self, expected_daily_minutes=480):
        self.expected_daily_minutes = expected_daily_minutes

    # -------------------------------------------------
    # 1️⃣ Reconstrucción de sesiones (soporta nocturnos)
    # -------------------------------------------------
    def reconstruct_sessions(self, logs):
        logs = sorted(logs, key=lambda x: (x.date, x.time))

        sessions = []
        open_entry = None

        for log in logs:
            dt = datetime.combine(log.date, log.time)

            if log.mark_type == 0:  # ENTRADA
                if open_entry is not None:
                    # Entrada duplicada → sesión inconsistente
                    sessions.append({
                        "start": open_entry,
                        "end": None,
                        "minutes": 0,
                        "inconsistent": True
                    })
                open_entry = dt

            elif log.mark_type == 1:  # SALIDA
                if open_entry is None:
                    # Salida sin entrada
                    sessions.append({
                        "start": None,
                        "end": dt,
                        "minutes": 0,
                        "inconsistent": True
                    })
                else:
                    worked_minutes = int((dt - open_entry).total_seconds() / 60)

                    if worked_minutes < 0:
                        sessions.append({
                            "start": open_entry,
                            "end": dt,
                            "minutes": 0,
                            "inconsistent": True
                        })
                    else:
                        sessions.append({
                            "start": open_entry,
                            "end": dt,
                            "minutes": worked_minutes,
                            "inconsistent": False
                        })

                    open_entry = None

        if open_entry is not None:
            sessions.append({
                "start": open_entry,
                "end": None,
                "minutes": 0,
                "inconsistent": True
            })

        return sessions

    # -------------------------------------------------
    # 2️⃣ Agrupación diaria
    # -------------------------------------------------
    def group_sessions_by_day(self, sessions):
        daily = defaultdict(list)

        for s in sessions:
            day = s["start"].date()  # jornada pertenece al día de entrada
            daily[day].append(s["minutes"])

        daily_minutes = {}

        for day, values in daily.items():
            daily_minutes[day] = sum(values)

        return daily_minutes

    # -------------------------------------------------
    # 3️⃣ Cálculo de features principales
    # -------------------------------------------------
    def compute_core_features(self, daily_minutes, inconsistencies):
        if not daily_minutes:
            return None

        minutes_list = list(daily_minutes.values())

        avg_daily = statistics.mean(minutes_list)
        median_daily = statistics.median(minutes_list)
        std_daily = statistics.stdev(minutes_list) if len(minutes_list) > 1 else 0
        min_daily = min(minutes_list)
        max_daily = max(minutes_list)

        underwork_rate = sum(
            1 for m in minutes_list if m < self.expected_daily_minutes
        ) / len(minutes_list)

        overwork_rate = sum(
            1 for m in minutes_list if m > self.expected_daily_minutes * 1.2
        ) / len(minutes_list)

        coefficient_variation = (
            std_daily / avg_daily if avg_daily > 0 else 0
        )

        return {
            "avg_daily_minutes": avg_daily,
            "median_daily_minutes": median_daily,
            "std_daily_minutes": std_daily,
            "min_daily_minutes": min_daily,
            "max_daily_minutes": max_daily,
            "underwork_rate": underwork_rate,
            "overwork_rate": overwork_rate,
            "coefficient_variation": coefficient_variation,
            "inconsistency_count": inconsistencies,
            "total_days": len(minutes_list)
        }

    # -------------------------------------------------
    # 4️⃣ Cálculo de tendencia
    # -------------------------------------------------
    def compute_trend(self, daily_minutes):
        if len(daily_minutes) < 2:
            return 0

        ordered_days = sorted(daily_minutes.keys())
        values = [daily_minutes[d] for d in ordered_days]

        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]

        return float(slope)

    # -------------------------------------------------
    # 5️⃣ Generación completa de features
    # -------------------------------------------------
    def generate_features(self, logs):
        sessions, inconsistencies = self.reconstruct_sessions(logs)

        daily_minutes = self.group_sessions_by_day(sessions)

        core = self.compute_core_features(daily_minutes, inconsistencies)

        if not core:
            return None

        trend = self.compute_trend(daily_minutes)

        core["trend_slope_minutes"] = trend
        core["volatility_index"] = abs(trend) * core["coefficient_variation"]

        # Señal temprana de caída abrupta
        if core["trend_slope_minutes"] < -30:
            core["sudden_drop_flag"] = 1
        else:
            core["sudden_drop_flag"] = 0

        return core