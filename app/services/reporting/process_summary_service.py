from datetime import datetime

from app.services.reporting.metrics_service import calcular_metricas_etapa, determinar_status


def build_process_response(process_id: str, data: dict) -> dict:
    start_time = data.get("start_time")
    end_time = data.get("end_time")

    if start_time and end_time:
        tiempo_total = round((end_time - start_time).total_seconds(), 4)
    elif start_time:
        tiempo_total = round((datetime.now() - start_time).total_seconds(), 4)
    else:
        tiempo_total = None

    metricas_descarga = calcular_metricas_etapa(data.get("downloads", []), "download_time_seconds")
    metricas_resize = calcular_metricas_etapa(data.get("resizes", []), "resize_time_seconds")
    metricas_formato = calcular_metricas_etapa(data.get("formats", []), "format_time_seconds")
    metricas_marca_agua = calcular_metricas_etapa(data.get("watermarks", []), "watermark_time_seconds")

    total_recibidos = len(data.get("request_data", {}).get("urls", []))
    total_errores = (
        metricas_descarga["total_fallidos"]
        + metricas_resize["total_fallidos"]
        + metricas_formato["total_fallidos"]
        + metricas_marca_agua["total_fallidos"]
    )
    total_exitosos = total_recibidos - metricas_descarga["total_fallidos"]
    porcentaje_exito = round((total_exitosos / total_recibidos) * 100, 2) if total_recibidos else 0.0
    porcentaje_fallo = round(100 - porcentaje_exito, 2)

    return {
        "informacion_general": {
            "process_id": process_id,
            "status": determinar_status(data),
            "start_time": start_time.isoformat() if start_time else None,
            "end_time": end_time.isoformat() if end_time else None,
            "tiempo_total_ejecucion": tiempo_total,
        },
        "metricas_por_etapa": {
            "descarga": metricas_descarga,
            "redimension": metricas_resize,
            "formato": metricas_formato,
            "marca_agua": metricas_marca_agua,
        },
        "resumen_global": {
            "total_archivos_recibidos": total_recibidos,
            "total_archivos_con_error": total_errores,
            "porcentaje_exito": porcentaje_exito,
            "porcentaje_fallo": porcentaje_fallo,
        },
    }
