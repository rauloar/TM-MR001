from datetime import datetime
from proceso.feature_engine import FeatureEngine
from proceso.behavior_engine import BehaviorEngine


class BehaviorProcessor:

    def __init__(self, session, expected_daily_minutes=480):
        self.session = session
        self.feature_engine = FeatureEngine(expected_daily_minutes)
        self.behavior_engine = BehaviorEngine(session)

    # -------------------------------------------------
    # Procesamiento completo por usuario
    # -------------------------------------------------
    def process_user(self, user_identifier, fecha_inicio=None, fecha_fin=None):
        from attendance.models import AttendanceLog

        # -------------------------------------------------
        # 1️⃣ Obtener logs del usuario
        # -------------------------------------------------
        query = self.session.query(AttendanceLog) \
            .filter(AttendanceLog.raw_identifier == user_identifier)

        logs = query.all()

        if not logs:
            return None

        # -------------------------------------------------
        # 2️⃣ Reconstruir sesiones (soporta nocturnos)
        # -------------------------------------------------
        sessions = self.feature_engine.reconstruct_sessions(logs)

        if not sessions:
            return None

        # -------------------------------------------------
        # 3️⃣ Asegurar tipos date correctos
        # -------------------------------------------------
        if isinstance(fecha_inicio, datetime):
            fecha_inicio = fecha_inicio.date()

        if isinstance(fecha_fin, datetime):
            fecha_fin = fecha_fin.date()

        # -------------------------------------------------
        # 4️⃣ Filtrar sesiones respetando selector
        #    Política: sesión pertenece al día de ENTRADA
        # -------------------------------------------------
        if fecha_inicio and fecha_fin:
            filtered_sessions = [
                s for s in sessions
                if s.get("start") and fecha_inicio <= s["start"].date() <= fecha_fin
            ]
        elif fecha_inicio:
            filtered_sessions = [
                s for s in sessions
                if s.get("start") and s["start"].date() >= fecha_inicio
            ]
        elif fecha_fin:
            filtered_sessions = [
                s for s in sessions
                if s.get("start") and s["start"].date() <= fecha_fin
            ]
        else:
            filtered_sessions = [s for s in sessions if s.get("start")]

        if not filtered_sessions:
            return None

        # -------------------------------------------------
        # 5️⃣ Recalcular inconsistencias SOLO del rango seleccionado
        # -------------------------------------------------
        inconsistencies = sum(
            1 for s in filtered_sessions if s.get("inconsistent", False)
        )

        # -------------------------------------------------
        # 6️⃣ Agrupar por día
        # -------------------------------------------------
        daily_minutes = self.feature_engine.group_sessions_by_day(filtered_sessions)

        if not daily_minutes:
            return None

        # -------------------------------------------------
        # 7️⃣ Calcular features principales
        # -------------------------------------------------
        core = self.feature_engine.compute_core_features(
            daily_minutes,
            inconsistencies
        )

        if not core:
            return None

        # -------------------------------------------------
        # 7️⃣ Calcular tendencia
        # -------------------------------------------------
        trend = self.feature_engine.compute_trend(daily_minutes)

        core["trend_slope_minutes"] = trend
        core["volatility_index"] = abs(trend) * core["coefficient_variation"]
        core["sudden_drop_flag"] = 1 if trend < -30 else 0

        # -------------------------------------------------
        # 8️⃣ Evaluar comportamiento (Rule Engine)
        # -------------------------------------------------
        evaluation = self.behavior_engine.evaluate(
             user_identifier,
             core,
             fecha_inicio,
             fecha_fin
        )

        # -------------------------------------------------
        # 9️⃣ Retornar resultado estructurado completo
        # -------------------------------------------------
        return {
            "user_identifier": user_identifier,
            "features": core,
            "score": evaluation.get("score"),
            "risk": evaluation.get("risk"),
            "triggered_rules": evaluation.get("triggered_rules", [])
        }