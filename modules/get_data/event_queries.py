from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

SQL_EVENTS_MIN = text("""
SELECT
    c.nom                                                AS nom,
    d.date_evenement                                     AS date,
    TRIM(BOTH ', ' FROM CONCAT_WS(', ',
        IF(ep.photobooth   = 1, 'photobooth',  NULL),
        IF(ep.miroirbooth  = 1, 'miroirbooth', NULL),
        IF(ep.videobooth   = 1, 'videobooth',  NULL),
        IF(ep.voguebooth   = 1, 'voguebooth',  NULL),
        IF(ep.ipadbooth    = 1, 'ipadbooth',   NULL),
        IF(ep.airbooth     = 1, 'airbooth',    NULL)
    ))                                                    AS product,
    e.status                                             AS status,
    TRIM(BOTH ', ' FROM CONCAT_WS(', ',
        IF(eo.MurFloral             = 1, 'MurFloral',              NULL),
        IF(eo.Phonebooth            = 1, 'Phonebooth',             NULL),
        IF(eo.LivreOr               = 1, 'LivreOr',                NULL),
        IF(eo.Fond360               = 1, 'Fond360',                NULL),
        IF(eo.PanneauBienvenue      = 1, 'PanneauBienvenue',       NULL),
        IF(eo.PhotographeVoguebooth = 1, 'PhotographeVoguebooth',  NULL),
        IF(eo.ImpressionVoguebooth  = 1, 'ImpressionVoguebooth',   NULL),
        IF(eo.DecorVoguebooth       = 1, 'DecorVoguebooth',        NULL),
        IF(eo.Holo3D                = 1, 'Holo3D',                 NULL)
    ))                                                    AS `option`,
    pp.sent                                              AS sent,
    et.directory_name                                    AS directory_name
FROM app_event e
JOIN app_client c                ON c.id = e.client_id
JOIN app_eventdetails d          ON d.id = e.event_details_id
LEFT JOIN app_eventproduct ep    ON ep.id = e.event_product_id
LEFT JOIN app_eventoption eo     ON eo.id = e.event_option_id
LEFT JOIN app_eventpostprestation pp ON pp.id = e.event_post_presta_id
LEFT JOIN app_eventtemplate et   ON et.id = e.event_template_id
ORDER BY d.date_evenement ASC, c.nom ASC
LIMIT :limit;
""")

async def fetch_min_events(db: AsyncSession, limit: int = 50):
    rows = (await db.execute(SQL_EVENTS_MIN, {"limit": limit})).mappings().all()
    return [
        {
            "nom": r["nom"],
            "date": r["date"].isoformat() if r["date"] else None,
            "product": r["product"] or None,
            "status": r["status"],
            "option": r["option"] or None,
            "sent": bool(r["sent"]) if r["sent"] is not None else None,
            "directory_name": r["directory_name"],
        }
        for r in rows
    ]
