from sqlalchemy import create_engine
import pandas as pd

# Configura la cadena de conexión a tu base de datos SQL Server
connection_string = "mssql+pyodbc://Proyectos:rrmJJR4NUrnhDH1@DESKTOP-PKKA1QA/618136_349343?driver=ODBC+Driver+17+for+SQL+Server"
engine = create_engine(connection_string)

# Lee los datos desde una tabla en SQL Server
query = """
SELECT 
    [mixCode],
	ag.[code] AS curing_time,
	sl.[value] AS settlement_value,
	sl.[unit] AS unit_settlement,
	CONCAT(em.[firstName], ' ', em.[middleName], ' ', em.[lastName], ' ' ,em.[secondLastName]) AS fullname,
	tr.[identification] AS mixercode,
	DATEDIFF(MINUTE, ord.[loadTime], ord.[toJobTime]) AS Worktoplant,
    CAST(SUM([loadSize]) AS DECIMAL(18,2)) AS loadSize,
    [aggregate1_name],
    CAST(SUM([aggregate1_target]) AS DECIMAL(18, 2)) AS aggregate1_target,
    CAST(SUM([aggregate1_actual]) AS DECIMAL(18, 2)) AS aggregate1_actual,

    [aggregate2_name],
    CAST(SUM([aggregate2_target]) AS DECIMAL(18, 2)) AS aggregate2_target,
    CAST(SUM([aggregate2_actual]) AS DECIMAL(18, 2)) AS aggregate2_actual,

    [aggregate3_name],
    CAST(SUM([aggregate3_target]) AS DECIMAL(18, 2)) AS aggregate3_target,
    CAST(SUM([aggregate3_actual]) AS DECIMAL(18, 2)) AS aggregate3_actual,

	[cement1_name],
	CAST(SUM([cement1_target]) AS DECIMAL(18,2)) AS cement1_target,
	CAST(SUM([cement1_actual]) AS DECIMAL(18,2)) AS cement1_actual,

	[cement2_name],
	CAST(SUM([cement2_target]) AS DECIMAL(18,2)) AS cement2_target,
	CAST(SUM([cement2_actual]) AS DECIMAL(18,2)) AS cement2_actual,

	[cement3_name],
	CAST(SUM([cement3_target]) AS DECIMAL(18,2)) AS cement3_target,
	CAST(SUM([cement3_actual]) AS DECIMAL(18,2)) AS cement3_actual,

    [admixture1_name],
    CAST(SUM([admixture1_target]) AS DECIMAL(18, 2)) AS admixture1_target,
    CAST(SUM([admixture1_actual]) AS DECIMAL(18, 2)) AS admixture1_actual,

    [admixture2_name],
    CAST(SUM([admixture2_target]) AS DECIMAL(18, 2)) AS admixture2_target,
    CAST(SUM([admixture2_actual]) AS DECIMAL(18, 2)) AS admixture2_actual,

    [admixture3_name],
    CAST(SUM([admixture3_target]) AS DECIMAL(18, 2)) AS admixture3_target,
    CAST(SUM([admixture3_actual]) AS DECIMAL(18, 2)) AS admixture3_actual,

    [admixture4_name],
    CAST(SUM([admixture4_target]) AS DECIMAL(18, 2)) AS admixture4_target,
    CAST(SUM([admixture4_actual]) AS DECIMAL(18, 2)) AS admixture4_actual,

    -- Consolidar aguas en un solo campo para cada tipo de valor
    CAST(SUM([water1_target]) + SUM([water2_target]) AS DECIMAL(18, 2)) AS total_water_target,

	CASE
		WHEN sa.[strengthUnit] = 2 THEN STR(sa.[strength] * 0.00689476, 18, 4) -- PSI a MPa
		WHEN sa.[strengthUnit] = 3 THEN STR(sa.[strength] * 0.0980665, 18, 4) -- kg/cm² a MPa
		ELSE sa.[strength]
	END AS strength_in_mpa,

    -- Calcular el water_to_cement_ratio
    CAST(
        CASE 
            WHEN (SUM([cement1_actual]) + SUM([cement2_actual]) + SUM([cement3_actual])) = 0 THEN NULL
            ELSE (SUM([water1_actual]) + SUM([water2_actual])) / (SUM([cement1_actual]) + SUM([cement2_actual]) + SUM([cement3_actual]))
        END AS DECIMAL(17, 16)
    ) AS water_to_cement_ratio

FROM 
    [618136_349343].[dbo].[tblBatch] AS tb
INNER JOIN 
    [CONCRETO4_True].[dbo].[tblProduct] AS tp ON tp.code = tb.mixCode
INNER JOIN
	[CONCRETO4_True].[dbo].[tblAge] AS ag ON ag.ageId = tp.ageId
INNER JOIN
	[CONCRETO4_True].[dbo].[tblSlump] AS sl ON sl.slumpId = tp.slumpId
INNER JOIN 
	[CONCRETO4_True].[dbo].[tblOrder] AS ord ON ord.batchNumber = tb.batchId
INNER JOIN
	[CONCRETO4_True].[dbo].[tblSample] AS sa ON sa.orderId = ord.orderId
INNER JOIN
	[CONCRETO4_True].[dbo].[tblTruck] AS tr ON tr.truckId = ord.truckId
INNER JOIN
	[CONCRETO4_True].[dbo].[tblEmployee] AS em ON em.employeeId = tr.employeeId 
WHERE 
    tb.[status] = 1
    AND tb.[isActive] = 1
	AND sl.isActive = 1
	AND NOT (
        [aggregate1_name] LIKE '%---%' OR
        [aggregate2_name] LIKE '%---%' OR
        [aggregate3_name] LIKE '%---%' OR
        [cement1_name] LIKE '%---%' OR
        [cement2_name] LIKE '%---%' OR
        [cement3_name] LIKE '%---%' OR
        [admixture1_name] LIKE '%---%' OR
        [admixture2_name] LIKE '%---%' OR
        [admixture3_name] LIKE '%---%' OR
        [admixture4_name] LIKE '%---%'
    )
	AND (
        [aggregate1_name] NOT LIKE '%NULL%' AND 
        [aggregate2_name] NOT LIKE '%NULL%' AND 
        [aggregate3_name] NOT LIKE '%NULL%' AND
        [cement1_name] NOT LIKE '%NULL%' AND 
        [cement2_name] NOT LIKE '%NULL%' AND 
        [cement3_name] NOT LIKE '%NULL%' AND 
        [admixture1_name] NOT LIKE '%NULL%' AND
        [admixture2_name] NOT LIKE '%NULL%' AND
        [admixture3_name] NOT LIKE '%NULL%' AND
        [admixture4_name] NOT LIKE '%NULL%' AND
        [water1_target] NOT LIKE '%NULL%' AND
        [water2_target] NOT LIKE '%NULL%' AND
		DATEDIFF(MINUTE, ord.[loadTime], ord.[toJobTime]) NOT LIKE '%NULL%' 
    )
GROUP BY 
    [mixCode], 
	ag.[code],
	sl.[value],
	sl.[unit],
	ord.[loadTime],
	ord.[toJobTime],
	sa.[strength],
	sa.[strengthUnit],
	em.[firstName],
	em.[middleName],
	em.[lastName],
	em.[secondLastName],
	tr.[identification],
    [aggregate1_name], [aggregate2_name], [aggregate3_name], [aggregate4_name], [aggregate5_name], 
	[cement1_name], [cement2_name], [cement3_name],
    [admixture1_name], [admixture2_name], [admixture3_name], [admixture4_name], [admixture5_name]
ORDER BY 
    [mixCode];

"""
df = pd.read_sql(query, engine)
df.to_csv("./csv/ConcretetestVoid.csv", index=False, sep=";")
