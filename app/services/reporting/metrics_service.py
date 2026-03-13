def calcular_metricas_etapa(registros: list, campo_tiempo: str):
    exitosos = [r for r in registros if "error" not in r]
    fallidos = [r for r in registros if "error" in r]
    tiempos = [r[campo_tiempo] for r in exitosos if campo_tiempo in r]

    total_acumulado = round(sum(tiempos), 4)
    promedio = round(total_acumulado / len(tiempos), 4) if tiempos else 0.0

    return {
        "total_procesados": len(exitosos),
        "total_fallidos": len(fallidos),
        "tiempo_total_acumulado": total_acumulado,
        "tiempo_promedio": promedio,
    }


def determinar_status(data: dict) -> str:
    if data["status"] == "EN_PROCESO":
        return "EN_PROCESO"

    total_errores = (
        data.get("download_errors", 0)
        + data.get("resize_errors", 0)
        + data.get("format_errors", 0)
        + data.get("watermark_errors", 0)
    )

    if data["status"] == "ERROR":
        return "FALLIDO"
    if total_errores > 0:
        return "COMPLETADO_CON_ERRORES"
    return "COMPLETADO"
