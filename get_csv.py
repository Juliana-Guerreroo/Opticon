from sqlalchemy import create_engine
import pandas as pd

# Configura la cadena de conexión a tu base de datos SQL Server
connection_string = "mssql+pyodbc://Proyectos:rrmJJR4NUrnhDH1@DESKTOP-PKKA1QA/618136_349343?driver=ODBC+Driver+17+for+SQL+Server"
engine = create_engine(connection_string)

# Lee los datos desde una tabla en SQL Server
query = """
SELECT 
    [mixCode],
    CAST(SUM([loadSize]) AS DECIMAL(28,2)) AS loadSize,
    [aggregate1_name],
    CAST(SUM([aggregate1_target]) AS DECIMAL(28, 2)) AS aggregate1_target,
    CAST(SUM([aggregate1_actual]) AS DECIMAL(28, 2)) AS aggregate1_actual,
    [aggregate2_name],
    CAST(SUM([aggregate2_target]) AS DECIMAL(28, 2)) AS aggregate2_target,
    CAST(SUM([aggregate2_actual]) AS DECIMAL(28, 2)) AS aggregate2_actual,
    [aggregate3_name],
    CAST(SUM([aggregate3_target]) AS DECIMAL(28, 2)) AS aggregate3_target,
    CAST(SUM([aggregate3_actual]) AS DECIMAL(28, 2)) AS aggregate3_actual,

    -- Consolidar cementos en un solo campo para cada tipo de valor
    CAST(SUM([cement1_target]) + SUM([cement2_target]) + SUM([cement3_target]) AS DECIMAL(28, 2)) AS total_cement_target,
    CAST(SUM([cement1_actual]) + SUM([cement2_actual]) + SUM([cement3_actual]) AS DECIMAL(28, 2)) AS total_cement_actual,

    [admixture1_name],
    CAST(SUM([admixture1_target]) AS DECIMAL(28, 2)) AS admixture1_target,
    CAST(SUM([admixture1_actual]) AS DECIMAL(28, 2)) AS admixture1_actual,

    [admixture2_name],
    CAST(SUM([admixture2_target]) AS DECIMAL(28, 2)) AS admixture2_target,
    CAST(SUM([admixture2_actual]) AS DECIMAL(28, 2)) AS admixture2_actual,

    [admixture3_name],
    CAST(SUM([admixture3_target]) AS DECIMAL(28, 2)) AS admixture3_target,
    CAST(SUM([admixture3_actual]) AS DECIMAL(28, 2)) AS admixture3_actual,

    [admixture4_name],
    CAST(SUM([admixture4_target]) AS DECIMAL(28, 2)) AS admixture4_target,
    CAST(SUM([admixture4_actual]) AS DECIMAL(28, 2)) AS admixture4_actual,

    -- Consolidar aguas en un solo campo para cada tipo de valor
    CAST(SUM([water1_target]) + SUM([water2_target]) AS DECIMAL(28, 2)) AS total_water_target,
    CAST(SUM([water1_actual]) + SUM([water2_actual]) AS DECIMAL(28, 2)) AS total_water_actual,

    -- Aplicar la conversión condicional en la columna Resistencia
    CAST(
        CASE 
            WHEN st.unit = 'MR' THEN st.value * 10.1972
            ELSE st.value
        END AS DECIMAL(28, 4)
    ) AS ResistenciaConvertida,

    -- Calcular el water_to_cement_ratio
    CAST(
        CASE 
            WHEN (SUM([cement1_actual]) + SUM([cement2_actual]) + SUM([cement3_actual])) = 0 THEN NULL
            ELSE (SUM([water1_actual]) + SUM([water2_actual])) / (SUM([cement1_actual]) + SUM([cement2_actual]) + SUM([cement3_actual]))
        END AS DECIMAL(38, 16)
    ) AS water_to_cement_ratio

FROM 
    [618136_349343].[dbo].[tblBatch] AS tb
full JOIN 
    [CONCRETO4_True].[dbo].[tblProduct] AS tp ON tp.code = tb.mixCode
full JOIN 
    [CONCRETO4_True].[dbo].[tblStrength] AS st ON st.strengthId = tp.strengthId
WHERE 
    [status] = 1
    AND tb.[isActive] = 1

GROUP BY 
    [mixCode], 
    [aggregate1_name], [aggregate2_name], [aggregate3_name], [aggregate4_name], [aggregate5_name], 
    [admixture1_name], [admixture2_name], [admixture3_name], [admixture4_name], [admixture5_name], 
    st.value, st.unit 
ORDER BY 
    [mixCode];

"""
df = pd.read_sql(query, engine)
df.to_csv("./csv/ConcretetestVoid.csv", index=False, sep=";")
