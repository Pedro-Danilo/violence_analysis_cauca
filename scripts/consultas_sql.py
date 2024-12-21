# Datos de geolocalizacion y poblacion 
geoloc_poblacion = """
    SELECT 
        md.dept_mpio_code AS codigo_dane,
        md.mupio_name AS nombre_municipio,
        md.geometry AS geometria_pol_mpio,
        md.mupal_head AS geometria_pol_capital,
        mpp.year,
        SUM(mpp.population) AS poblacion
    FROM 
        public.municipalities_dane md
    JOIN 
        public.departments_dane dd ON md.dept_code = dd.dept_code
    JOIN 
        public.municipal_population_projections_dane mpp ON md.dept_mpio_code = mpp.dane_code
    WHERE 
        dd.dept_name = 'CAUCA'
        AND mpp.year BETWEEN 2019 AND 2023
    GROUP BY 
        md.dept_mpio_code, md.mupio_name, md.geometry, md.mupal_head, mpp.year
    ORDER BY 
        md.mupio_name, mpp.year;
    """

frontera_agricula = """
    WITH agricultural_data AS (
    SELECT 
        dane_code,
        frontier_type,
        SUM(area_ha) AS total_area
    FROM 
        public.agricultural_frontier_minagricultura
    WHERE 
        dane_code IN (
            SELECT dept_mpio_code 
            FROM public.municipalities_dane md
            JOIN public.departments_dane dd 
            ON md.dept_code = dd.dept_code
            WHERE dd.dept_name = 'CAUCA'
        )
    GROUP BY 
        dane_code, frontier_type
)

    -- Replicación de datos para los años 2019-2023
    SELECT 
        a.dane_code,
        EXTRACT(YEAR FROM generate_series('2019-01-01'::date, '2023-01-01'::date, '1 year')) AS anio,
        SUM(CASE WHEN a.frontier_type = 'CONDICIONADA' THEN a.total_area ELSE 0 END) AS area_condicionada,
        SUM(CASE WHEN a.frontier_type = 'NO CONDICIONADA' THEN a.total_area ELSE 0 END) AS area_no_condicionada
    FROM 
        agricultural_data a
    GROUP BY 
        a.dane_code, anio
    ORDER BY 
        a.dane_code, anio;    
"""

mineria_aluvion = """
WITH replicated_data AS (
    -- Seleccionamos los datos originales del año 2020 para replicarlos
    SELECT
        dane_code,
        ha_with_permit,
        ha_peremit_in_process,
        ha_under_illegal_explotation,
        year
    FROM
        public.alluvial_gold_mining_minminas
    WHERE
        dane_code LIKE '19%' -- Filtra solo los municipios del Cauca
        AND year = 2020 -- Selecciona el año 2020 para replicarlo
),
data_with_years AS (
    -- Incluimos los datos originales de 2019
    SELECT
        dane_code,
        ha_with_permit,
        ha_peremit_in_process,
        ha_under_illegal_explotation,
        year
    FROM
        public.alluvial_gold_mining_minminas
    WHERE
        dane_code LIKE '19%' -- Filtra solo los municipios del Cauca
        AND year = 2019 -- Selecciona el año 2019
    UNION ALL
    -- Incluimos los datos originales de 2020
    SELECT
        dane_code,
        ha_with_permit,
        ha_peremit_in_process,
        ha_under_illegal_explotation,
        year
    FROM replicated_data
    UNION ALL
    -- Replicamos los datos de 2020 para los años 2021-2023
    SELECT
        dane_code,
        ha_with_permit,
        ha_peremit_in_process,
        ha_under_illegal_explotation,
        2021 AS year
    FROM replicated_data
    UNION ALL
    SELECT
        dane_code,
        ha_with_permit,
        ha_peremit_in_process,
        ha_under_illegal_explotation,
        2022 AS year
    FROM replicated_data
    UNION ALL
    SELECT
        dane_code,
        ha_with_permit,
        ha_peremit_in_process,
        ha_under_illegal_explotation,
        2023 AS year
    FROM replicated_data
)

    SELECT *
    FROM data_with_years
    ORDER BY dane_code, year;    
"""

arrestos_mineria_ilegal = """
    SELECT 
        dane_code,
        year_of_incident,
        SUM(amount) AS total_arrests
    FROM 
        public.arrests_for_ilegal_mining_mindefensa
    WHERE 
        dane_code LIKE '19%'  -- Filtro para los municipios del Cauca
        AND year_of_incident BETWEEN 2019 AND 2023  -- Filtro para los años 2019-2023
    GROUP BY 
        dane_code, year_of_incident
    ORDER BY 
        dane_code, year_of_incident;    
"""

incautaciones_basuco = """
    SELECT 
    dane_code, 
    year_of_incident, 
    SUM(amount) AS total_amount_confiscated
    FROM 
        public.basuco_confiscations_mindefensa
    WHERE 
        dane_code LIKE '19%' 
        AND year_of_incident BETWEEN 2019 AND 2023
    GROUP BY 
        dane_code, year_of_incident
    ORDER BY 
        dane_code, year_of_incident;
"""

victimas_conflicto_sievcac = """
    WITH replicated_data AS (
-- Agrupamos los datos por municipio y año
        SELECT
            dane_code,
            year,
            SUM(injured_civilians) AS total_injured_civilians,
            SUM(total_number_of_victims) AS total_victims,
            COUNT(*) AS case_count
        FROM public.cases_armed_conflict_sievcac
        WHERE dane_code LIKE '19%'  -- Filtrar municipios del Cauca
        AND year BETWEEN 2019 AND 2022  -- Filtrar años 2019-2022
        GROUP BY dane_code, year
)
-- Mantener los datos originales y añadir un nuevo año 2023 replicando los datos de 2022
    SELECT 
        dane_code,
        year,
        total_injured_civilians,
        total_victims,
        case_count
    FROM replicated_data

    UNION ALL

    -- Replicar los datos del año 2022 para crear el año 2023
    SELECT 
        dane_code,
        2023 AS year,  -- Nuevo año 2023
        total_injured_civilians,
        total_victims,
        case_count
    FROM replicated_data
    WHERE year = 2022  -- Solo replicamos los datos de 2022

    ORDER BY dane_code, year;
"""

tasas_alfabetas_censo_2018 = """
    WITH censo_cauca AS (
        SELECT
            cod_dep_mpio AS codigo_dane,
            COUNT(*) AS total_personas,
            SUM(CASE WHEN p_alfabeta = 1 THEN 1 ELSE 0 END) AS personas_alfabetas,
            SUM(CASE WHEN p_alfabeta = 2 THEN 1 ELSE 0 END) AS personas_analfabetas
        FROM public.censo_2018_personas_dane
        WHERE cod_dep_mpio LIKE '19%'
        GROUP BY cod_dep_mpio
)
    SELECT
        codigo_dane,
        total_personas,
        (personas_alfabetas::decimal / total_personas) AS tasa_alfabetismo,
        (personas_analfabetas::decimal / total_personas) AS tasa_analfabetismo,
        generate_series(2019, 2023) AS year
    FROM censo_cauca;
"""

tasa_desempleo_censo_2018 = """
    WITH tasas_desempleo AS (
        SELECT 
            cod_dep_mpio AS codigo_dane,
            COUNT(CASE WHEN p_trabajo = 4 THEN 1 END) * 100.0 / 
            NULLIF(COUNT(CASE WHEN p_trabajo IN (1, 2, 3, 4) THEN 1 END), 0) AS tasa_desempleo_2018
        FROM 
            public.censo_2018_personas_dane
        WHERE 
            cod_dep_mpio LIKE '19%'  -- Solo municipios del Cauca
        GROUP BY 
            cod_dep_mpio
)
    SELECT 
        codigo_dane,
        generate_series(2019, 2023) AS ano,
        tasa_desempleo_2018 AS tasa_desempleo
    FROM 
        tasas_desempleo;

"""

indicadores_hogares_censo_2018 = """
    WITH datos_cauca AS (
        SELECT
            cod_dep_mpio AS codigo_dane,
            COUNT(*) AS numero_hogares,
            AVG(h_nro_dormit / NULLIF(ha_tot_per, 0)) AS hacinamiento_promedio,
            AVG(ha_tot_per / NULLIF(h_nro_cuartos, 0)) AS densidad_habitacional,
            SUM(CASE WHEN h_donde_prepalim IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*)::float AS tasa_acceso_a_cocina,
            SUM(CASE WHEN h_agua_cocin IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*)::float AS tasa_acceso_a_agua_para_cocinar
        FROM
            public.censo_hogares_2018_dane
        WHERE
            cod_dep_mpio LIKE '19%'  -- Filtro para municipios del Cauca
        GROUP BY
            cod_dep_mpio
    )
    SELECT
        codigo_dane,
        numero_hogares,
        hacinamiento_promedio,
        densidad_habitacional,
        tasa_acceso_a_cocina,
        tasa_acceso_a_agua_para_cocinar,
        year
    FROM
        datos_cauca,
        GENERATE_SERIES(2019, 2023) AS year -- Replicar los datos para los años 2019-2023
    ORDER BY
        codigo_dane, year;
"""

indicadores_serv_pub_viviendas_censo_2018 = """
    WITH cobertura_servicios AS (
        SELECT
            cod_dep_mpio,
            (SUM(CASE WHEN va_ee = 1 THEN 1 ELSE 0 END)::float / COUNT(CASE WHEN va_ee IN (1, 2) THEN 1 END)) AS electrico,
            (SUM(CASE WHEN vb_acu = 1 THEN 1 ELSE 0 END)::float / COUNT(CASE WHEN vb_acu IN (1, 2) THEN 1 END)) AS acueducto,
            (SUM(CASE WHEN vc_alc = 1 THEN 1 ELSE 0 END)::float / COUNT(CASE WHEN vc_alc IN (1, 2) THEN 1 END)) AS alcantarillado,
            (SUM(CASE WHEN vd_gas = 1 THEN 1 ELSE 0 END)::float / COUNT(CASE WHEN vd_gas IN (1, 2) THEN 1 END)) AS gas_natural,
            (SUM(CASE WHEN ve_recbas = 1 THEN 1 ELSE 0 END)::float / COUNT(CASE WHEN ve_recbas IN (1, 2) THEN 1 END)) AS recoleccion_basuras,
            (SUM(CASE WHEN vf_internet = 1 THEN 1 ELSE 0 END)::float / COUNT(CASE WHEN vf_internet IN (1, 2) THEN 1 END)) AS internet,
            COUNT(*) AS total_viviendas
        FROM censo_viviendas_2018_dane
        WHERE cod_dep_mpio LIKE '19%'  -- Municipios del Cauca (códigos DANE que comienzan con '19')
        GROUP BY cod_dep_mpio
)
    SELECT
        cs.cod_dep_mpio,
        cs.electrico,
        cs.acueducto,
        cs.alcantarillado,
        cs.gas_natural,
        cs.recoleccion_basuras,
        cs.internet,
        cs.total_viviendas,
        anio
    FROM cobertura_servicios cs,
    LATERAL GENERATE_SERIES(2019, 2023) AS anio;
"""

otros_indicadores_viviendas_censo_2018 = """
    WITH viviendas_cauca AS (
        SELECT
            cod_dep_mpio, 
            COUNT(id) AS total_viviendas,
            AVG(v_tot_hog) AS promedio_hogares_vivienda,
            SUM(CASE WHEN va1_estrato = 1 THEN 1 ELSE 0 END) * 1.0 / COUNT(id) AS porcentaje_estrato_1,
            SUM(CASE WHEN va1_estrato = 2 THEN 1 ELSE 0 END) * 1.0 / COUNT(id) AS porcentaje_estrato_2,
            SUM(CASE WHEN va1_estrato = 3 THEN 1 ELSE 0 END) * 1.0 / COUNT(id) AS porcentaje_estrato_3,
            SUM(CASE WHEN v_mat_pared IN (1, 2, 3) THEN 1 ELSE 0 END) * 1.0 / COUNT(id) AS porcentaje_pared_adecuada,
            SUM(CASE WHEN v_mat_pared IN (4, 5, 6, 7, 8, 9) THEN 1 ELSE 0 END) * 1.0 / COUNT(id) AS porcentaje_pared_inadecuada,
            SUM(CASE WHEN v_mat_piso IN (1, 2, 3) THEN 1 ELSE 0 END) * 1.0 / COUNT(id) AS porcentaje_piso_adecuado,
            SUM(CASE WHEN v_mat_piso IN (4, 5, 6) THEN 1 ELSE 0 END) * 1.0 / COUNT(id) AS porcentaje_piso_inadecuado
        FROM
            public.censo_viviendas_2018_dane
        WHERE
            cod_dep_mpio LIKE '19%'
        GROUP BY
            cod_dep_mpio
)

-- Aplicar valores para los años 2019-2023
    SELECT 
        cod_dep_mpio,
        promedio_hogares_vivienda,
        porcentaje_estrato_1,
        porcentaje_estrato_2,
        porcentaje_estrato_3,
        porcentaje_pared_adecuada,
        porcentaje_pared_inadecuada,
        porcentaje_piso_adecuado,
        porcentaje_piso_inadecuado,
        year
    FROM
        viviendas_cauca,
        generate_series(2019, 2023) AS year;
"""

cultivos_coca = """
    WITH coca_data AS (
        SELECT
            dane_code AS codigo_dane,
            UNNEST(ARRAY[2019, 2020, 2021, 2022, 2023]) AS year,
            UNNEST(ARRAY["2019", "2020", "2021", "2022", "2022"]) AS cantidad_coca_cultivada
        FROM
            public.coca_plantations_minjusticia
        WHERE
            dane_code LIKE '19%'
)
    SELECT * FROM coca_data
    ORDER BY codigo_dane, year;
"""

base_coca_confiscada_mindef ="""
    SELECT 
    codigo_dane, 
    year_of_incident AS year, 
        SUM(amount) AS cantidad_base_coca_confiscada
    FROM 
        public.cocaine_base_confiscations_mindefensa
    WHERE 
        codigo_dane LIKE '19%' -- Filtra municipios del Cauca
        AND year_of_incident BETWEEN 2019 AND 2023 -- Filtra el periodo 2019-2023
    GROUP BY 
        codigo_dane, year_of_incident
    ORDER BY 
        codigo_dane, year_of_incident;
"""

coca_confiscada_mindef = """
    SELECT 
    dane_code, 
    year_of_incident AS year, 
        SUM(amount) AS cantidad_coca_confiscada
    FROM 
        public.cocaine_confiscations_mindefensa
    WHERE 
        dane_code LIKE '19%' -- Filtra municipios del Cauca
        AND year_of_incident BETWEEN 2019 AND 2023 -- Filtra el periodo 2019-2023
    GROUP BY 
        dane_code, year_of_incident
    ORDER BY 
        dane_code, year_of_incident;
"""

mariguana_confiscada_mindef = """
    SELECT 
    dane_code, 
    year_of_incident AS year, 
        SUM(amount) AS cantidad_mariguana_confiscada
    FROM 
        public.confiscation_of_mariajuana_mindefensa
    WHERE 
        dane_code LIKE '19%' -- Filtra municipios del Cauca
        AND year_of_incident BETWEEN 2019 AND 2023 -- Filtra el periodo 2019-2023
    GROUP BY 
        dane_code, year_of_incident
    ORDER BY 
        dane_code, year_of_incident;
"""

noticias_de_crimenes_fiscalia = """
    SELECT 
    dept_mpio_code AS codigo_dane,
    year_of_incident AS ano,
    COUNT(CASE WHEN crime_group = 'AMENAZAS' THEN 1 END) AS amenazas_casos_fiscalia,
    COUNT(CASE WHEN crime_group = 'DELITOS SEXUALES' THEN 1 END) AS delitos_sexuales_casos_fiscalia,
    COUNT(CASE WHEN crime_group = 'DESAPARICION FORZADA' THEN 1 END) AS desaparicion_forzada_casos_fiscalia,
    COUNT(CASE WHEN crime_group = 'DESPLAZAMIENTO' THEN 1 END) AS desplazamiento_casos_fiscalia,
    COUNT(CASE WHEN crime_group = 'ESTAFA' THEN 1 END) AS estafa_casos_fiscalia,
    COUNT(CASE WHEN crime_group = 'EXTORSION' THEN 1 END) AS extorsion_casos_fiscalia,
    COUNT(CASE WHEN crime_group = 'HURTO' THEN 1 END) AS hurto_casos_fiscalia,
    COUNT(CASE WHEN crime_group = 'PERSONAS Y BIENES PROTEGIDOS POR EL DIH' THEN 1 END) AS personas_bienes_dih_casos_fiscalia,
    COUNT(CASE WHEN crime_group = 'RECLUTAMIENTO ILICITO' THEN 1 END) AS reclutamiento_ilicito_casos_fiscalia,
    COUNT(CASE WHEN crime_group = 'VIOLENCIA INTRAFAMILIAR' THEN 1 END) AS violencia_intrafamiliar_casos_fiscalia,

    -- Agrupación para CORRUPCION
    COUNT(CASE WHEN crime_group IN ('CORRUPCION ADMINISTRATIVA', 'CORRUPCION ELECTORAL', 'CORRUPCION JUDICIAL', 'CORRUPCION PRIVADA', 'CORRUPCION TRIBUTARIA') THEN 1 END) AS corrupcion_casos_fiscalia,

    -- Agrupación para HOMICIDIOS
    COUNT(CASE WHEN crime_group IN ('FEMINICIDIO', 'HOMICIDIO CULPOSO', 'HOMICIDIO DOLOSO') THEN 1 END) AS homicidios_casos_fiscalia,

    -- Agrupación para LESIONES PERSONALES
    COUNT(CASE WHEN crime_group IN ('LESIONES PERSO AGENTES QUIMICOS', 'LESIONES PERSONALES', 'LESIONES PERSONALES CULPOSAS') THEN 1 END) AS lesiones_personales_casos_fiscalia,

    -- Agrupación para SECUESTRO
    COUNT(CASE WHEN crime_group IN ('SECUESTRO EXTORSIVO', 'SECUESTRO SIMPLE') THEN 1 END) AS secuestro_casos_fiscalia,

    -- Agrupación para OTROS DELITOS
    COUNT(CASE WHEN crime_group NOT IN ('AMENAZAS', 'DELITOS SEXUALES', 'DESAPARICION FORZADA', 'DESPLAZAMIENTO', 'ESTAFA', 'EXTORSION', 
                                        'HURTO', 'PERSONAS Y BIENES PROTEGIDOS POR EL DIH', 'RECLUTAMIENTO ILICITO', 'VIOLENCIA INTRAFAMILIAR', 
                                        'CORRUPCION ADMINISTRATIVA', 'CORRUPCION ELECTORAL', 'CORRUPCION JUDICIAL', 'CORRUPCION PRIVADA', 'CORRUPCION TRIBUTARIA',
                                        'FEMINICIDIO', 'HOMICIDIO CULPOSO', 'HOMICIDIO DOLOSO', 
                                        'LESIONES PERSO AGENTES QUIMICOS', 'LESIONES PERSONALES', 'LESIONES PERSONALES CULPOSAS', 
                                        'SECUESTRO EXTORSIVO', 'SECUESTRO SIMPLE') THEN 1 END) AS otros_delitos_casos_fiscalia

    FROM 
        public.crime_news_fiscalia
    WHERE 
        dept_mpio_code LIKE '19%'  -- Solo municipios del Cauca
        AND year_of_incident BETWEEN 2019 AND 2023  -- Filtrar por el periodo 2019-2023
    GROUP BY 
        dept_mpio_code, year_of_incident
    ORDER BY 
        dept_mpio_code, year_of_incident;
"""

indiciados_crimenes_fiscalia = """
    SELECT 
        m.dept_mpio_code AS codigo_dane,
        i.year_of_incident,
        
        -- AMENAZAS
        SUM(CASE WHEN i.crime_group = 'AMENAZAS' THEN i.total_indicted ELSE 0 END) AS indiciados_fisc_amenazas,

        -- DELITOS SEXUALES
        SUM(CASE WHEN i.crime_group = 'DELITOS SEXUALES' THEN i.total_indicted ELSE 0 END) AS indiciados_fisc_delitos_sexuales,

        -- DESAPARICION FORZADA
        SUM(CASE WHEN i.crime_group = 'DESAPARICION FORZADA' THEN i.total_indicted ELSE 0 END) AS indiciados_fisc_desaparicion_forzada,

        -- DESPLAZAMIENTO
        SUM(CASE WHEN i.crime_group = 'DESPLAZAMIENTO' THEN i.total_indicted ELSE 0 END) AS indiciados_fisc_desplazamiento,

        -- ESTAFA
        SUM(CASE WHEN i.crime_group = 'ESTAFA' THEN i.total_indicted ELSE 0 END) AS indiciados_fisc_estafa,

        -- EXTORSION
        SUM(CASE WHEN i.crime_group = 'EXTORSION' THEN i.total_indicted ELSE 0 END) AS indiciados_fisc_extorsion,

        -- HURTO
        SUM(CASE WHEN i.crime_group = 'HURTO' THEN i.total_indicted ELSE 0 END) AS indiciados_fisc_hurto,

        -- PERSONAS Y BIENES PROTEGIDOS POR EL DIH
        SUM(CASE WHEN i.crime_group = 'PERSONAS Y BIENES PROTEGIDOS POR EL DIH' THEN i.total_indicted ELSE 0 END) AS indiciados_fisc_dih,

        -- RECLUTAMIENTO ILICITO
        SUM(CASE WHEN i.crime_group = 'RECLUTAMIENTO ILICITO' THEN i.total_indicted ELSE 0 END) AS indiciados_fisc_reclutamiento_ilicito,

        -- VIOLENCIA INTRAFAMILIAR
        SUM(CASE WHEN i.crime_group = 'VIOLENCIA INTRAFAMILIAR' THEN i.total_indicted ELSE 0 END) AS indiciados_fisc_violencia_intrafamiliar,

        -- CORRUPCION (Agrupa varios grupos de crimen relacionados con corrupción)
        SUM(CASE WHEN i.crime_group IN ('CORRUPCION ADMINISTRATIVA', 'CORRUPCION ELECTORAL', 'CORRUPCION JUDICIAL', 'CORRUPCION PRIVADA', 'CORRUPCION TRIBUTARIA') 
            THEN i.total_indicted ELSE 0 END) AS indiciados_fisc_corrupcion,

        -- HOMICIDIOS (Agrupa feminicidio, homicidio culposo y homicidio doloso)
        SUM(CASE WHEN i.crime_group IN ('FEMINICIDIO', 'HOMICIDIO CULPOSO', 'HOMICIDIO DOLOSO') 
            THEN i.total_indicted ELSE 0 END) AS indiciados_fisc_homicidios,

        -- LESIONES PERSONALES (Agrupa varias categorías de lesiones personales)
        SUM(CASE WHEN i.crime_group IN ('LESIONES PERSO AGENTES QUIMICOS', 'LESIONES PERSONALES', 'LESIONES PERSONALES CULPOSAS') 
            THEN i.total_indicted ELSE 0 END) AS indiciados_fisc_lesiones_personales,

        -- SECUESTRO (Agrupa secuestro extorsivo y secuestro simple)
        SUM(CASE WHEN i.crime_group IN ('SECUESTRO EXTORSIVO', 'SECUESTRO SIMPLE') 
            THEN i.total_indicted ELSE 0 END) AS indiciados_fisc_secuestro,

        -- OTROS DELITOS (Agrupa los crímenes que no están en las categorías anteriores)
        SUM(CASE WHEN i.crime_group NOT IN ('AMENAZAS', 'DELITOS SEXUALES', 'DESAPARICION FORZADA', 'DESPLAZAMIENTO', 'ESTAFA', 
            'EXTORSION', 'HURTO', 'PERSONAS Y BIENES PROTEGIDOS POR EL DIH', 'RECLUTAMIENTO ILICITO', 'VIOLENCIA INTRAFAMILIAR', 
            'CORRUPCION ADMINISTRATIVA', 'CORRUPCION ELECTORAL', 'CORRUPCION JUDICIAL', 'CORRUPCION PRIVADA', 'CORRUPCION TRIBUTARIA', 
            'FEMINICIDIO', 'HOMICIDIO CULPOSO', 'HOMICIDIO DOLOSO', 'LESIONES PERSO AGENTES QUIMICOS', 'LESIONES PERSONALES', 
            'LESIONES PERSONALES CULPOSAS', 'SECUESTRO EXTORSIVO', 'SECUESTRO SIMPLE') 
            THEN i.total_indicted ELSE 0 END) AS indiciados_fisc_otros_delitos

    FROM 
        public.indicted_count_fiscalia i
    JOIN 
        public.municipalities_dane m ON i.dept_mpio_code = m.dept_mpio_code
    WHERE 
        i.year_of_incident BETWEEN 2019 AND 2023
        AND m.dept_mpio_code LIKE '19%' -- Filtra por municipios del Cauca
    GROUP BY 
        m.dept_mpio_code, i.year_of_incident
    ORDER BY 
        m.dept_mpio_code, i.year_of_incident;
"""

victimas_crimen_fiscalia ="""
    SELECT 
        year_of_incident,
        dept_mpio_code,
        SUM(CASE 
            WHEN crime_group = 'AMENAZAS' THEN total_victims 
            ELSE 0 
        END) AS victim_fisc_amenazas,
        SUM(CASE 
            WHEN crime_group = 'DELITOS SEXUALES' THEN total_victims 
            ELSE 0 
        END) AS victim_fisc_delitos_sexuales,
        SUM(CASE 
            WHEN crime_group = 'DESAPARICION FORZADA' THEN total_victims 
            ELSE 0 
        END) AS victim_fisc_desaparicion_forzada,
        SUM(CASE 
            WHEN crime_group = 'DESPLAZAMIENTO' THEN total_victims 
            ELSE 0 
        END) AS victim_fisc_desplazamiento,
        SUM(CASE 
            WHEN crime_group = 'ESTAFA' THEN total_victims 
            ELSE 0 
        END) AS victim_fisc_estafa,
        SUM(CASE 
            WHEN crime_group = 'EXTORSION' THEN total_victims 
            ELSE 0 
        END) AS victim_fisc_extorsion,
        SUM(CASE 
            WHEN crime_group = 'HURTO' THEN total_victims 
            ELSE 0 
        END) AS victim_fisc_hurto,
        SUM(CASE 
            WHEN crime_group = 'PERSONAS Y BIENES PROTEGIDOS POR EL DIH' THEN total_victims 
            ELSE 0 
        END) AS victim_fisc_personas_bienes_dih,
        SUM(CASE 
            WHEN crime_group = 'RECLUTAMIENTO ILICITO' THEN total_victims 
            ELSE 0 
        END) AS victim_fisc_reclutamiento_ilicito,
        SUM(CASE 
            WHEN crime_group = 'VIOLENCIA INTRAFAMILIAR' THEN total_victims 
            ELSE 0 
        END) AS victim_fisc_violencia_intrafamiliar,
        -- Agrupación de categorías de corrupción
        SUM(CASE 
            WHEN crime_group IN ('CORRUPCION ADMINISTRATIVA', 'CORRUPCION ELECTORAL', 'CORRUPCION JUDICIAL', 'CORRUPCION PRIVADA', 'CORRUPCION TRIBUTARIA') 
            THEN total_victims 
            ELSE 0 
        END) AS victim_fisc_corrupcion,
        -- Agrupación de homicidios
        SUM(CASE 
            WHEN crime_group IN ('FEMINICIDIO', 'HOMICIDIO CULPOSO', 'HOMICIDIO DOLOSO') 
            THEN total_victims 
            ELSE 0 
        END) AS victim_fisc_homicidios,
        -- Agrupación de lesiones personales
        SUM(CASE 
            WHEN crime_group IN ('LESIONES PERSO AGENTES QUIMICOS', 'LESIONES PERSONALES', 'LESIONES PERSONALES CULPOSAS') 
            THEN total_victims 
            ELSE 0 
        END) AS victim_fisc_lesiones_personales,
        -- Agrupación de secuestro
        SUM(CASE 
            WHEN crime_group IN ('SECUESTRO EXTORSIVO', 'SECUESTRO SIMPLE') 
            THEN total_victims 
            ELSE 0 
        END) AS victim_fisc_secuestro,
        -- Agrupación de otros delitos
        SUM(CASE 
            WHEN crime_group NOT IN (
                'AMENAZAS', 'DELITOS SEXUALES', 'DESAPARICION FORZADA', 'DESPLAZAMIENTO', 'ESTAFA', 
                'EXTORSION', 'HURTO', 'PERSONAS Y BIENES PROTEGIDOS POR EL DIH', 
                'RECLUTAMIENTO ILICITO', 'VIOLENCIA INTRAFAMILIAR', 
                'CORRUPCION ADMINISTRATIVA', 'CORRUPCION ELECTORAL', 'CORRUPCION JUDICIAL', 
                'CORRUPCION PRIVADA', 'CORRUPCION TRIBUTARIA', 
                'FEMINICIDIO', 'HOMICIDIO CULPOSO', 'HOMICIDIO DOLOSO', 
                'LESIONES PERSO AGENTES QUIMICOS', 'LESIONES PERSONALES', 'LESIONES PERSONALES CULPOSAS', 
                'SECUESTRO EXTORSIVO', 'SECUESTRO SIMPLE') 
            THEN total_victims 
            ELSE 0 
        END) AS victim_fisc_otros_delitos
    FROM victim_count_fiscalia
    WHERE dept_mpio_code LIKE '19%'  -- Filtrar municipios del Cauca
    AND year_of_incident BETWEEN 2019 AND 2023  -- Filtrar años 2019-2023
    GROUP BY year_of_incident, dept_mpio_code
    ORDER BY year_of_incident, dept_mpio_code;

"""

fuerza_pub_victim_mindef = """
    SELECT 
        dane_code AS codigo_dane,
        year_of_incident AS ano,
        SUM(amount) AS soldados_victim_mindef
    FROM 
        public.deaths_in_public_forces_mindefensa
    WHERE 
        dane_code LIKE '19%'  -- Filtrar solo los municipios del Cauca
        AND year_of_incident BETWEEN 2019 AND 2023  -- Filtrar entre 2019 y 2023
    GROUP BY 
        dane_code, year_of_incident
    ORDER BY 
        dane_code, year_of_incident;
"""

lab_destruidos_mindef =""" 
    SELECT 
        dane_code,
        year_of_incident AS year,
        SUM(amount) AS lab_destruidos_mindef
    FROM 
        public.destroyed_labs_mindefensa
    WHERE 
        year_of_incident BETWEEN 2019 AND 2023
        AND dane_code LIKE '19%'
    GROUP BY 
        dane_code, year_of_incident
    ORDER BY 
        dane_code, year;
"""

crimen_ambientales_mindef = """ 
    SELECT 
        dane_code AS codigo_dane,
        year_of_incident AS anio,
        SUM(amount) AS crimen_ambientales_mindef
    FROM 
        public.environmental_crimes_mindefensa
    WHERE 
        dane_code LIKE '19%' -- Filtrar solo municipios del Cauca
        AND year_of_incident BETWEEN 2019 AND 2023 -- Filtrar por años
    GROUP BY 
        dane_code, year_of_incident
    ORDER BY 
        codigo_dane, anio;
"""

casos_extorsion_mindef = """ 
    SELECT 
        e.dane_code AS codigo_dane,
        e.year_of_incident AS año,
        SUM(e.amount) AS casos_extorsion_mindef
    FROM 
        public.extortion_mindefensa e
    WHERE 
        e.year_of_incident BETWEEN 2019 AND 2023
        AND e.dane_code LIKE '19%'  -- Filtrar municipios del Cauca
    GROUP BY 
        e.dane_code, e.year_of_incident
    ORDER BY 
        e.dane_code, e.year_of_incident;
"""

casos_minas_intervenidas_mindef =""" 
    SELECT 
        e.dane_code AS codigo_dane,
        e.year_of_incident AS año,
        SUM(e.amount) AS minas_interv_mindef
    FROM 
        public.intervened_mines_mindefensa e
    WHERE 
        e.year_of_incident BETWEEN 2019 AND 2023
        AND e.dane_code LIKE '19%'  -- Filtrar municipios del Cauca
    GROUP BY 
        e.dane_code, e.year_of_incident
    ORDER BY 
        e.dane_code, e.year_of_incident;
"""

casos_secuestro_mindef =  """ 
    SELECT 
        e.dane_code AS codigo_dane,
        e.year_of_incident AS año,
        SUM(e.amount) AS secuestro_mindef
    FROM 
        public.kidnapping_mindefensa e
    WHERE 
        e.year_of_incident BETWEEN 2019 AND 2023
        AND e.dane_code LIKE '19%'  -- Filtrar municipios del Cauca
    GROUP BY 
        e.dane_code, e.year_of_incident
    ORDER BY 
        e.dane_code, e.year_of_incident;
"""

casos_pirateria_terrestre_mindef = """ 
    SELECT 
        e.dane_code AS codigo_dane,
        e.year_of_incident AS año,
        SUM(e.amount) AS pirateria_terrest_mindef
    FROM 
        public.land_piracy_mindefensa e
    WHERE 
        e.year_of_incident BETWEEN 2019 AND 2023
        AND e.dane_code LIKE '19%'  -- Filtrar municipios del Cauca
    GROUP BY 
        e.dane_code, e.year_of_incident
    ORDER BY 
        e.dane_code, e.year_of_incident;
"""

incaut_insumos_liqu_mindef = """ 
    SELECT 
        e.dane_code AS codigo_dane,
        e.year_of_incident AS año,
        SUM(e.amount) AS incaut_insumos_liq_mindef
    FROM 
        public.liquid_inputs_confiscations_mindefensa e
    WHERE 
        e.year_of_incident BETWEEN 2019 AND 2023
        AND e.dane_code LIKE '19%'  -- Filtrar municipios del Cauca
    GROUP BY 
        e.dane_code, e.year_of_incident
    ORDER BY 
        e.dane_code, e.year_of_incident;
"""

masacres_mindef = """ 
    SELECT 
        e.dane_code AS codigo_dane,
        e.year_of_incident AS año,
        SUM(e.amount) AS masacres_mindef
    FROM 
        public.massacres_mindefensa e
    WHERE 
        e.year_of_incident BETWEEN 2019 AND 2023
        AND e.dane_code LIKE '19%'  -- Filtrar municipios del Cauca
    GROUP BY 
        e.dane_code, e.year_of_incident
    ORDER BY 
        e.dane_code, e.year_of_incident;
"""

asesinatos_mindef = """ 
    SELECT 
        e.dane_code AS codigo_dane,
        e.year_of_incident AS año,
        SUM(e.amount) AS asesinatos_mindef
    FROM 
        public.murders_mindefensa e
    WHERE 
        e.year_of_incident BETWEEN 2019 AND 2023
        AND e.dane_code LIKE '19%'  -- Filtrar municipios del Cauca
    GROUP BY 
        e.dane_code, e.year_of_incident
    ORDER BY 
        e.dane_code, e.year_of_incident;
"""

casos_terrorismo_mindef = """ 
    SELECT 
        e.dane_code AS codigo_dane,
        e.year_of_incident AS año,
        SUM(e.amount) AS casos_terror_mindef
    FROM 
        public.terrorism_mindefensa e
    WHERE 
        e.year_of_incident BETWEEN 2019 AND 2023
        AND e.dane_code LIKE '19%'  -- Filtrar municipios del Cauca
    GROUP BY 
        e.dane_code, e.year_of_incident
    ORDER BY 
        e.dane_code, e.year_of_incident;
"""

robos_entid_financ = """ 
    SELECT 
        e.dane_code AS codigo_dane,
        e.year_of_incident AS año,
        SUM(e.amount) AS robo_entid_finan_mindef
    FROM 
        public.theft_from_financial_institutions_mindefensa e
    WHERE 
        e.year_of_incident BETWEEN 2019 AND 2023
        AND e.dane_code LIKE '19%'  -- Filtrar municipios del Cauca
    GROUP BY 
        e.dane_code, e.year_of_incident
    ORDER BY 
        e.dane_code, e.year_of_incident;
"""

robos_a_personas_mindef = """ 
    SELECT 
        e.dane_code AS codigo_dane,
        e.year_of_incident AS año,
        SUM(e.amount) AS robo_a_personas_mindef
    FROM 
        public.theft_from_people_mindefensa e
    WHERE 
        e.year_of_incident BETWEEN 2019 AND 2023
        AND e.dane_code LIKE '19%'  -- Filtrar municipios del Cauca
    GROUP BY 
        e.dane_code, e.year_of_incident
    ORDER BY 
        e.dane_code, e.year_of_incident;
"""

violencia_domestica_polinal = """ 
    SELECT 
        dane_code AS codigo_dane,
        year_of_incident AS año,
        SUM(amount) AS violenc_domest_polinal
    FROM 
        public.domestic_violence_polinal
    WHERE 
        dane_code LIKE '19%' -- Filtra los municipios del Cauca
        AND year_of_incident BETWEEN 2019 AND 2023 -- Filtra los años 2019-2023
    GROUP BY 
        dane_code, year_of_incident
    ORDER BY 
        dane_code, year_of_incident;
"""

incautacion_drogas_polinal = """ 
    SELECT 
        dane_code AS codigo_dane,
        year_of_incident AS año,
        SUM(amount) AS incautacion_drogas_poli
    FROM 
        public.drug_seizure_polinal
    WHERE 
        dane_code LIKE '19%' -- Filtra los municipios del Cauca
        AND year_of_incident BETWEEN 2019 AND 2023 -- Filtra los años 2019-2023
    GROUP BY 
        dane_code, year_of_incident
    ORDER BY 
        dane_code, year_of_incident;
"""

robo_viviendas_negocios_polinal = """ 
    SELECT 
        dane_code AS codigo_dane,
        year_of_incident AS año,
        SUM(amount) AS robo_viv_neg_polinal
    FROM 
        public.home_and_business_theft_polinal
    WHERE 
        dane_code LIKE '19%' -- Filtra los municipios del Cauca
        AND year_of_incident BETWEEN 2019 AND 2023 -- Filtra los años 2019-2023
    GROUP BY 
        dane_code, year_of_incident
    ORDER BY 
        dane_code, year_of_incident;
"""

lesiones_personales_polinal = """ 
    SELECT 
        dane_code AS codigo_dane,
        year_of_incident AS año,
        SUM(amount) AS les_personales_polinal
    FROM 
        public.personal_injury_polinal
    WHERE 
        dane_code LIKE '19%' -- Filtra los municipios del Cauca
        AND year_of_incident BETWEEN 2019 AND 2023 -- Filtra los años 2019-2023
    GROUP BY 
        dane_code, year_of_incident
    ORDER BY 
        dane_code, year_of_incident;
"""

delitos_sexuales_polinal = """ 
    SELECT 
        dane_code AS codigo_dane,
        year_of_incident AS año,
        SUM(amount) AS delito_sexual_polinal
    FROM 
        public.sexual_crimes_polinal
    WHERE 
        dane_code LIKE '19%' -- Filtra los municipios del Cauca
        AND year_of_incident BETWEEN 2019 AND 2023 -- Filtra los años 2019-2023
    GROUP BY 
        dane_code, year_of_incident
    ORDER BY 
        dane_code, year_of_incident;
"""

casos_terrorismo_polinal = """ 
    SELECT 
        dane_code AS codigo_dane,
        year_of_incident AS año,
        SUM(amount) AS terrorismo_polinal
    FROM 
        public.terrorism_crimes_polinal
    WHERE 
        dane_code LIKE '19%' -- Filtra los municipios del Cauca
        AND year_of_incident BETWEEN 2019 AND 2023 -- Filtra los años 2019-2023
    GROUP BY 
        dane_code, year_of_incident
    ORDER BY 
        dane_code, year_of_incident;
"""

casos_robos_polinal = """ 
    SELECT 
        dane_code AS codigo_dane,
        year_of_incident AS año,
        SUM(amount) AS robos_polinal
    FROM 
        public.theft_by_modality_polinal
    WHERE 
        dane_code LIKE '19%' -- Filtra los municipios del Cauca
        AND year_of_incident BETWEEN 2019 AND 2023 -- Filtra los años 2019-2023
    GROUP BY 
        dane_code, year_of_incident
    ORDER BY 
        dane_code, year_of_incident;
"""

casos_amenazas_polinal =  """ 
    SELECT 
        dane_code AS codigo_dane,
        year_of_incident AS año,
        SUM(amount) AS amenazas_polinal
    FROM 
        public.threat_crimes_polinal
    WHERE 
        dane_code LIKE '19%' -- Filtra los municipios del Cauca
        AND year_of_incident BETWEEN 2019 AND 2023 -- Filtra los años 2019-2023
    GROUP BY 
        dane_code, year_of_incident
    ORDER BY 
        dane_code, year_of_incident;
"""

robo_vehiculos_polinal = """ 
    SELECT 
        dane_code AS codigo_dane,
        year_of_incident AS año,
        SUM(amount) AS robo_vehiculos_polinal
    FROM 
        public.vehicle_theft_polinal
    WHERE 
        dane_code LIKE '19%' -- Filtra los municipios del Cauca
        AND year_of_incident BETWEEN 2019 AND 2023 -- Filtra los años 2019-2023
    GROUP BY 
        dane_code, year_of_incident
    ORDER BY 
        dane_code, year_of_incident;
"""

armas_confiscadas_polinal = """ 
    SELECT 
        dane_code AS codigo_dane,
        year_of_incident AS año,
        SUM(amount) AS armas_confis_polinal
    FROM 
        public.weapons_confiscation_polinal
    WHERE 
        dane_code LIKE '19%' -- Filtra los municipios del Cauca
        AND year_of_incident BETWEEN 2019 AND 2023 -- Filtra los años 2019-2023
    GROUP BY 
        dane_code, year_of_incident
    ORDER BY 
        dane_code, year_of_incident;
"""

primera_infancia_mined = """ 
    SELECT 
        dane_code AS codigo_dane,
        year,
        SUM(ind_1_icbf_children) AS ninos_icbf,
        SUM(ind_2_prescholar_children) AS ninos_prescolar
    FROM 
        public.early_childhood_indicators_mineducacion
    WHERE 
        dane_code LIKE '19%'  -- Filtramos por municipios del Cauca
        AND year BETWEEN 2019 AND 2023  -- Filtramos por el periodo 2019-2023
    GROUP BY 
        dane_code, year
    ORDER BY 
        dane_code, year;
"""

indicadores_educacion_bas_med_mineduc = """ 
    SELECT 
        dane_code,
        year,
        SUM(poblacion_5_16) AS poblacion_5_16,
        AVG(tasa_matricula_5_16) AS tasa_matricula_5_16,
        AVG(cobertura_neta) AS cobertura_neta,
        AVG(cobertura_bruta) AS cobertura_bruta,
        AVG(desercion) AS desercion,
        AVG(aprobacion) AS aprobacion
    FROM 
        educational_indicators_mineducacion
    WHERE 
        dane_code LIKE '19%' 
        AND year BETWEEN 2019 AND 2023
    GROUP BY 
        dane_code, year
    ORDER BY 
        dane_code, year;
"""

numero_muertes_med_legal = """ 
    SELECT 
        year_of_incident AS anio,
        dane_code AS codigo_dane,
        COUNT(*) AS num_muertes_medlegal
    FROM 
        public.fatal_injuries_med_legal
    WHERE 
        year_of_incident BETWEEN 2019 AND 2023
        AND dane_code LIKE '19%'
    GROUP BY 
        year_of_incident, dane_code
    ORDER BY 
        year_of_incident, dane_code;
"""

reporte_personas_perdidas = """ 
    SELECT 
        dane_code, 
        year_of_incident, 
        COUNT(id) AS reporte_desap_medlegal
    FROM 
        public.missing_people_med_legal
    WHERE 
        dane_code LIKE '19%'  -- Filtra los municipios del Cauca
        AND year_of_incident BETWEEN 2019 AND 2023  -- Filtra el periodo 2019-2023
    GROUP BY 
        dane_code, 
        year_of_incident
    ORDER BY 
        dane_code, 
        year_of_incident;
"""

reporte_lesiones_no_fatales_med_legal = """ 
    SELECT
        dane_code AS codigo_dane,
        year_of_incident AS anio,
        
        -- Conteo para el campo 'violencia_intrafamiliar_ml'
        SUM(CASE 
            WHEN cause_of_injury IN (
                'VIOLENCIA INTRAFAMILIAR ENTRE OTROS FAMILIARES',
                'VIOLENCIA INTRAFAMILIAR CONTRA NINOS NINAS Y ADOLESCENT',
                'VIOLENCIA INTRAFAMILIAR CONTRA EL ADULTO MAYO',
                'VIOLENCIA DE PAREJA'
            ) THEN 1 ELSE 0 END) AS violencia_intrafamiliar_ml,

        -- Conteo para el campo 'violencia_interpersonal_med'
        SUM(CASE 
            WHEN cause_of_injury = 'VIOLENCIA INTERPERSONAL'
            THEN 1 ELSE 0 END) AS violencia_interpersonal_ml,

        -- Conteo para el campo 'lesiones_accidentales_ml'
        SUM(CASE 
            WHEN cause_of_injury IN ('LESIONES EN ACCIDENTE DE TRANSITO', 'LESIONES ACCIDENTALES')
            THEN 1 ELSE 0 END) AS lesiones_accidentales_ml,

        -- Conteo para el campo 'presunto_delit_sexual_ml'
        SUM(CASE 
            WHEN cause_of_injury = 'EXAMENES MEDICO LEGALES POR PRESUNTO DELITO SEXUAL'
            THEN 1 ELSE 0 END) AS presunto_delit_sexual_ml

    FROM
        public.non_fatal_injuries_med_legal

    WHERE
        -- Filtrar solo municipios del Cauca (código DANE que empieza con '19')
        dane_code LIKE '19%'
        -- Filtrar el rango de años 2019 a 2023
        AND year_of_incident BETWEEN 2019 AND 2023

    GROUP BY
        dane_code, year_of_incident

    ORDER BY
        dane_code, year_of_incident;
""" 

afiliados_sss_adres = """ 
    WITH base_data AS (
        SELECT 
            codigo_dane,
            SUM(CASE WHEN tps_rgm_nombre = 'CONTRIBUTIVO' THEN cantidad ELSE 0 END) AS afil_contributivo,
            SUM(CASE WHEN tps_rgm_nombre = 'SUBSIDIADO' THEN cantidad ELSE 0 END) AS afil_subsidiado
        FROM 
            public.health_insurance_affiliated_adres
        WHERE 
            codigo_dane LIKE '19%'  -- Filtra municipios del Cauca
        GROUP BY 
            codigo_dane
)

    SELECT 
        codigo_dane,
        afil_contributivo,
        afil_subsidiado,
        year
    FROM 
        base_data,
        GENERATE_SERIES(2019, 2023) AS year  -- Replica la información para los años 2019-2023
    ORDER BY 
        codigo_dane, 
        year;
"""

num_solicit_reclacion_tierras_minagricultura = """
    WITH years AS (
        SELECT 2019 AS year UNION
        SELECT 2020 UNION
        SELECT 2021 UNION
        SELECT 2022 UNION
        SELECT 2023
)

    SELECT 
        lc.codigodane AS codigo_dane,
        y.year AS ano,
        SUM(lc.numerodesolicitantes) AS total_solicitantes
    FROM 
        public.land_restitution_claims_minagricultura lc
    JOIN 
        years y ON TRUE
    WHERE 
        lc.codigodane LIKE '19%'  -- Solo los municipios del Cauca
    GROUP BY 
        lc.codigodane, y.year
    ORDER BY 
        lc.codigodane, y.year;
"""

cabezas_ganado_minagricultura = """
    WITH livestock_data AS (
        SELECT
            dane_code,
            year,
            CASE 
                WHEN species IN ('OVINOS', 'BUFALOS') THEN 'cabezas_ovinos'
                WHEN species = 'EQUINOS' THEN 'cabezas_equinos'
                WHEN species = 'CAPRINOS' THEN 'cabezas_caprinos'
            END AS species_group,
            total
        FROM
            public.livestock_count_minagricultura
        WHERE
            dane_code LIKE '19%' -- Filtra municipios del Cauca
            AND year IN (2019, 2020, 2021) -- Filtra por los años que tienen datos
),
    aggregated_data AS (
        SELECT
            dane_code,
            year,
            SUM(CASE WHEN species_group = 'cabezas_ovinos' THEN total ELSE 0 END) AS cabezas_ovinos,
            SUM(CASE WHEN species_group = 'cabezas_equinos' THEN total ELSE 0 END) AS cabezas_equinos,
            SUM(CASE WHEN species_group = 'cabezas_caprinos' THEN total ELSE 0 END) AS cabezas_caprinos
        FROM
            livestock_data
        GROUP BY
            dane_code, year
)
    -- Agrega los datos de 2019, 2020, 2021 y genera los datos para 2022 y 2023 replicando 2021
    SELECT
        dane_code,
        year,
        cabezas_ovinos,
        cabezas_equinos,
        cabezas_caprinos
    FROM
        aggregated_data
-- UNION con los años generados (2022 y 2023) replicando los valores de 2021
    UNION ALL
    SELECT
        dane_code,
        gs.year,
        ad.cabezas_ovinos,
        ad.cabezas_equinos,
        ad.cabezas_caprinos
    FROM
        aggregated_data ad
        CROSS JOIN GENERATE_SERIES(2022, 2023) AS gs(year)
    WHERE
        ad.year = 2021
    ORDER BY
        dane_code, year;
"""

indicadores_mortal_morbil_minsalud = """
WITH cauca_data AS (
    -- Extraer los datos de los municipios del Cauca (dane_code empieza con 19)
    SELECT 
        dane_code,
        year,
        indicator_name,
        indicator_values
    FROM public.mortality_and_morbidity_rates_minsalud
    WHERE dane_code LIKE '19%' 
    AND year BETWEEN 2019 AND 2020
    AND indicator_name IN (
        'TASA DE MORTALIDAD POR DESNUTRICION EN MENORES DE 5 ANOS',
        'TASA DE MORTALIDAD GENERAL',
        'TASA DE MORTALIDAD EN NINOS MENORES DE 5 ANOS POR ENFERMEDAD DIARREICA AGUDA',
        'TASA DE MORTALIDAD EN LA NINEZ (MENORES DE 5 ANOS DE EDAD)',
        'PORCENTAJE DE NACIDOS VIVOS CON BAJO PESO AL NACER'
    )
),
-- Replicar los valores del año 2020 para los años 2021, 2022 y 2023
replicated_data AS (
    SELECT 
        dane_code,
        year,
        indicator_name,
        indicator_values
    FROM cauca_data
    UNION ALL
    SELECT 
        dane_code,
        2021 AS year,
        indicator_name,
        indicator_values
    FROM cauca_data
    WHERE year = 2020
    UNION ALL
    SELECT 
        dane_code,
        2022 AS year,
        indicator_name,
        indicator_values
    FROM cauca_data
    WHERE year = 2020
    UNION ALL
    SELECT 
        dane_code,
        2023 AS year,
        indicator_name,
        indicator_values
    FROM cauca_data
    WHERE year = 2020
)
-- Consolidar los datos en columnas por cada indicador
SELECT 
    dane_code,
    year,
    -- Usar COALESCE para devolver 0 si el valor es NULL
    COALESCE(MAX(CASE WHEN indicator_name = 'TASA DE MORTALIDAD POR DESNUTRICION EN MENORES DE 5 ANOS' THEN indicator_values END), 0) AS tasa_mort_desnutricion,
    COALESCE(MAX(CASE WHEN indicator_name = 'TASA DE MORTALIDAD GENERAL' THEN indicator_values END), 0) AS tasa_mort_general,
    COALESCE(MAX(CASE WHEN indicator_name = 'TASA DE MORTALIDAD EN NINOS MENORES DE 5 ANOS POR ENFERMEDAD DIARREICA AGUDA' THEN indicator_values END), 0) AS tasa_mort_diarr,
    COALESCE(MAX(CASE WHEN indicator_name = 'TASA DE MORTALIDAD EN LA NINEZ (MENORES DE 5 ANOS DE EDAD)' THEN indicator_values END), 0) AS tasa_mort_ninez,
    COALESCE(MAX(CASE WHEN indicator_name = 'PORCENTAJE DE NACIDOS VIVOS CON BAJO PESO AL NACER' THEN indicator_values END), 0) AS porc_bajo_peso_nacer
FROM replicated_data
GROUP BY dane_code, year
ORDER BY dane_code, year;
"""

indicadores_personas_sisben = """
    WITH data_sisben AS (
        SELECT
            cod_mpio,
            COUNT(CASE WHEN h_5 = 1 THEN 1 END) AS per_IPM_Sisben,
            COUNT(CASE WHEN i6 = 1 THEN 1 END) AS casos_trab_infan_Sisben,
            COUNT(CASE WHEN i8 = 1 THEN 1 END) AS per_tab_inf_Sisben,
            COUNT(CASE WHEN i14 = 1 THEN 1 END) AS per_haci_critico_Sisben
        FROM public.sisben_iv_personas_dnp
        WHERE cod_mpio LIKE '19%'
        GROUP BY cod_mpio
)
    SELECT 
        cod_mpio,
        per_IPM_Sisben,
        casos_trab_infan_Sisben,
        per_tab_inf_Sisben,
        per_haci_critico_Sisben,
        year
    FROM data_sisben, 
    UNNEST(ARRAY[2019, 2020, 2021, 2022, 2023]) AS year
    ORDER BY cod_mpio, year;
"""

num_hogares_viviendas_sisben = """
WITH hogares AS (
    SELECT cod_mpio, 
           COUNT(*) AS hogares_sisbenizados
    FROM public.sisben_iv_hogares_dnp
    WHERE cod_mpio LIKE '19%' -- Municipios del Cauca
    GROUP BY cod_mpio
),
viviendas AS (
    SELECT cod_mpio, 
           COUNT(*) AS viviendas_sisbenizados
    FROM public.sisben_iv_viviendas_dnp
    WHERE cod_mpio LIKE '19%' -- Municipios del Cauca
    GROUP BY cod_mpio
),
replica_anos AS (
    SELECT cod_mpio, 
           hogares_sisbenizados, 
           viviendas_sisbenizados, 
           ano
    FROM hogares
    JOIN viviendas USING (cod_mpio)
    CROSS JOIN generate_series(2019, 2023) AS ano -- Replicamos para los años 2019-2023
)
SELECT cod_mpio, 
       ano, 
       hogares_sisbenizados, 
       viviendas_sisbenizados
FROM replica_anos
ORDER BY cod_mpio, ano;

"""

conteo_unidad_victimas = """
WITH victimas_cauca AS (
    SELECT
        LEFT(dane_code, 5) AS codigo_dane,
        SUM(people_per_declaration) AS vict_por_declarac_uv,
        SUM(number_of_victims) AS vict_ubicadas_uv,
        SUM(people_under_attention) AS vict_en_atencion_uv,
        SUM(number_of_events) AS vict_por_eventos_uv
    FROM public.victims_by_type_of_crime_unidadvictimas
    WHERE dane_code LIKE '19%' -- Filtrar solo municipios del Cauca
    GROUP BY LEFT(dane_code, 5)
)
SELECT 
    codigo_dane,
    vict_por_declarac_uv,
    vict_ubicadas_uv,
    vict_en_atencion_uv,
    vict_por_eventos_uv,
    year
FROM victimas_cauca,
LATERAL (
    VALUES
        (2019),
        (2020),
        (2021),
        (2022),
        (2023)
) AS year_data(year)
ORDER BY codigo_dane, year;
"""

consultas = {
 'geoloc_poblacion': geoloc_poblacion,
 'frontera_agricula': frontera_agricula,
 'mineria_aluvion': mineria_aluvion,
 'arrestos_mineria_ilegal': arrestos_mineria_ilegal,
 'incautaciones_basuco': incautaciones_basuco,
 'victimas_conflicto_sievcac': victimas_conflicto_sievcac,
 'tasa_desempleo_censo_2018': tasa_desempleo_censo_2018,
 'tasas_alfabetas_censo_2018': tasas_alfabetas_censo_2018,
 'indicadores_hogares_censo_2018': indicadores_hogares_censo_2018,
 'indicadores_serv_pub_viviendas_censo_2018': indicadores_serv_pub_viviendas_censo_2018,
 'otros_indicadores_viviendas_censo_2018': otros_indicadores_viviendas_censo_2018,
 'cultivos_coca': cultivos_coca,
 'base_coca_confiscada_mindef': base_coca_confiscada_mindef,
 'coca_confiscada_mindef': coca_confiscada_mindef,
 'mariguana_confiscada_mindef': mariguana_confiscada_mindef,
 'noticias_de_crimenes_fiscalia': noticias_de_crimenes_fiscalia,
 'indiciados_crimenes_fiscalia': indiciados_crimenes_fiscalia,
 'victimas_crimen_fiscalia': victimas_crimen_fiscalia,
 'fuerza_pub_victim_mindef': fuerza_pub_victim_mindef,
 'lab_destruidos_mindef': lab_destruidos_mindef,
 'crimen_ambientales_mindef': crimen_ambientales_mindef,
 'casos_extorsion_mindef': casos_extorsion_mindef,
 'casos_minas_intervenidas_mindef': casos_minas_intervenidas_mindef,
 'casos_secuestro_mindef': casos_secuestro_mindef,
 'casos_pirateria_terrestre_mindef': casos_pirateria_terrestre_mindef,
 'incaut_insumos_liqu_mindef': incaut_insumos_liqu_mindef,
 'masacres_mindef': masacres_mindef,
 'asesinatos_mindef': asesinatos_mindef,
 'casos_terrorismo_mindef': casos_terrorismo_mindef,
 'robos_entid_financ': robos_entid_financ,
 'robos_a_personas_mindef': robos_a_personas_mindef,
 'violencia_domestica_polinal': violencia_domestica_polinal,
 'incautacion_drogas_polinal':incautacion_drogas_polinal,
 'robo_viviendas_negocios_polinal':robo_viviendas_negocios_polinal,
 'lesiones_personales_polinal': lesiones_personales_polinal,
 'delitos_sexuales_polinal': delitos_sexuales_polinal,
 'casos_terrorismo_polinal': casos_terrorismo_polinal,
 'casos_robos_polinal': casos_robos_polinal,
 'casos_amenazas_polinal': casos_amenazas_polinal,
 'robo_vehiculos_polinal': robo_vehiculos_polinal,
 'armas_confiscadas_polinal': armas_confiscadas_polinal,
 'primera_infancia_mined': primera_infancia_mined,
 'indicadores_educacion_bas_med_mineduc': indicadores_educacion_bas_med_mineduc,
 'numero_muertes_med_legal': numero_muertes_med_legal,
 'reporte_personas_perdidas': reporte_personas_perdidas,
 'reporte_lesiones_no_fatales_med_legal':reporte_lesiones_no_fatales_med_legal,
 'afiliados_sss_adres': afiliados_sss_adres,
 'num_solicit_reclacion_tierras_minagricultura': num_solicit_reclacion_tierras_minagricultura,
 'indicadores_mortal_morbil_minsalud': indicadores_mortal_morbil_minsalud,
 'indicadores_personas_sisben': indicadores_personas_sisben,
 'num_hogares_viviendas_sisben': num_hogares_viviendas_sisben,
 'conteo_unidad_victimas': conteo_unidad_victimas,
   
}
print(len(consultas))