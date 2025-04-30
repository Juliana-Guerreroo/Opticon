-- Eliminar las claves foráneas de las tablas que dependen de otras

-- tblMixer
IF EXISTS (SELECT * FROM sys.foreign_keys WHERE object_id = OBJECT_ID(N'[dbo].[FK__tblMixer__mixerConditionId]'))
BEGIN
    ALTER TABLE tblMixer DROP CONSTRAINT FK__tblMixer__mixerConditionId;
END

-- tblConcrete
IF EXISTS (SELECT * FROM sys.foreign_keys WHERE object_id = OBJECT_ID(N'[dbo].[FK__tblConcrete__plantId]'))
BEGIN
    ALTER TABLE tblConcrete DROP CONSTRAINT FK__tblConcrete__plantId;
END

IF EXISTS (SELECT * FROM sys.foreign_keys WHERE object_id = OBJECT_ID(N'[dbo].[FK__tblConcrete__buildingId]'))
BEGIN
    ALTER TABLE tblConcrete DROP CONSTRAINT FK__tblConcrete__buildingId;
END

-- tblCement
IF EXISTS (SELECT * FROM sys.foreign_keys WHERE object_id = OBJECT_ID(N'[dbo].[FK__tblCement__cementTypeId]'))
BEGIN
    ALTER TABLE tblCement DROP CONSTRAINT FK__tblCement__cementTypeId;
END

IF EXISTS (SELECT * FROM sys.foreign_keys WHERE object_id = OBJECT_ID(N'[dbo].[FK__tblCement__cementCompositionId]'))
BEGIN
    ALTER TABLE tblCement DROP CONSTRAINT FK__tblCement__cementCompositionId;
END

-- tblAggregated
IF EXISTS (SELECT * FROM sys.foreign_keys WHERE object_id = OBJECT_ID(N'[dbo].[FK__tblAggregated__aggregatedTypeId]'))
BEGIN
    ALTER TABLE tblAggregated DROP CONSTRAINT FK__tblAggregated__aggregatedTypeId;
END

IF EXISTS (SELECT * FROM sys.foreign_keys WHERE object_id = OBJECT_ID(N'[dbo].[FK__tblAggregated__aggregatedShapeId]'))
BEGIN
    ALTER TABLE tblAggregated DROP CONSTRAINT FK__tblAggregated__aggregatedShapeId;
END

-- tblAdditive
IF EXISTS (SELECT * FROM sys.foreign_keys WHERE object_id = OBJECT_ID(N'[dbo].[FK__tblAdditive__additiveTypeId]'))
BEGIN
    ALTER TABLE tblAdditive DROP CONSTRAINT FK__tblAdditive__additiveTypeId;
END

-- Eliminar las tablas en el orden correcto

-- Eliminar la tabla tblBuilding si existe
IF OBJECT_ID('tblBuilding', 'U') IS NOT NULL
BEGIN
    DROP TABLE tblBuilding;
END

-- Eliminar la tabla tblMixerBuilding si existe
IF OBJECT_ID('tblMixerBuilding', 'U') IS NOT NULL
BEGIN
    DROP TABLE tblMixerBuilding;
END

-- Eliminar la tabla tblMixerCondition si existe
IF OBJECT_ID('tblMixerCondition', 'U') IS NOT NULL
BEGIN
    DROP TABLE tblMixerCondition;
END

-- Eliminar la tabla tblMixer si existe
IF OBJECT_ID('tblMixer', 'U') IS NOT NULL
BEGIN
    DROP TABLE tblMixer;
END

-- Eliminar la tabla tblMixType si existe
IF OBJECT_ID('tblMixType', 'U') IS NOT NULL
BEGIN
    DROP TABLE tblMixType;
END

-- Eliminar la tabla tblPlant si existe
IF OBJECT_ID('tblPlant', 'U') IS NOT NULL
BEGIN
    DROP TABLE tblPlant;
END

-- Eliminar la tabla tblConcrete si existe
IF OBJECT_ID('tblConcrete', 'U') IS NOT NULL
BEGIN
    DROP TABLE tblConcrete;
END

-- Eliminar la tabla tblWaterConcrete si existe
IF OBJECT_ID('tblWaterConcrete', 'U') IS NOT NULL
BEGIN
    DROP TABLE tblWaterConcrete;
END

-- Eliminar la tabla tblCementType si existe
IF OBJECT_ID('tblCementType', 'U') IS NOT NULL
BEGIN
    DROP TABLE tblCementType;
END

-- Eliminar la tabla tblCementComposition si existe
IF OBJECT_ID('tblCementComposition', 'U') IS NOT NULL
BEGIN
    DROP TABLE tblCementComposition;
END

-- Eliminar la tabla tblCement si existe
IF OBJECT_ID('tblCement', 'U') IS NOT NULL
BEGIN
    DROP TABLE tblCement;
END

-- Eliminar la tabla tblCementConcrete si existe
IF OBJECT_ID('tblCementConcrete', 'U') IS NOT NULL
BEGIN
    DROP TABLE tblCementConcrete;
END

-- Eliminar la tabla tblAggregatedType si existe
IF OBJECT_ID('tblAggregatedType', 'U') IS NOT NULL
BEGIN
    DROP TABLE tblAggregatedType;
END

-- Eliminar la tabla tblAggregatedShape si existe
IF OBJECT_ID('tblAggregatedShape', 'U') IS NOT NULL
BEGIN
    DROP TABLE tblAggregatedShape;
END

-- Eliminar la tabla tblAggregated si existe
IF OBJECT_ID('tblAggregated', 'U') IS NOT NULL
BEGIN
    DROP TABLE tblAggregated;
END

-- Eliminar la tabla tblAggregatedConcrete si existe
IF OBJECT_ID('tblAggregatedConcrete', 'U') IS NOT NULL
BEGIN
    DROP TABLE tblAggregatedConcrete;
END

-- Eliminar la tabla tblAggregatedTexture si existe
IF OBJECT_ID('tblAggregatedTexture', 'U') IS NOT NULL
BEGIN
    DROP TABLE tblAggregatedTexture;
END

-- Eliminar la tabla tblAdditiveType si existe
IF OBJECT_ID('tblAdditiveType', 'U') IS NOT NULL
BEGIN
    DROP TABLE tblAdditiveType;
END

-- Eliminar la tabla tblAdditive si existe
IF OBJECT_ID('tblAdditive', 'U') IS NOT NULL
BEGIN
    DROP TABLE tblAdditive;
END

-- Eliminar la tabla tblAdditiveConcrete si existe
IF OBJECT_ID('tblAdditiveConcrete', 'U') IS NOT NULL
BEGIN
    DROP TABLE tblAdditiveConcrete;
END


CREATE TABLE tblBuilding(
buildingId UNIQUEIDENTIFIER,
locatiónId UNIQUEIDENTIFIER,
cureConcrete decimal(18,2),
PRIMARY KEY (buildingId),
--FOREIGN KEY (locatiónId) REFERENCES CONCRETO4_TRUE.dbo.tblLocation(locationId)
);

CREATE TABLE tblMixerBuilding(
mixerBuildingId UNIQUEIDENTIFIER,
buildingId UNIQUEIDENTIFIER,
mixerId UNIQUEIDENTIFIER,
PRIMARY KEY (mixerBuildingId),
FOREIGN KEY (buildingId) REFERENCES tblBuilding(buildingId)
);

CREATE TABLE tblMixerCondition(
mixerConditionId UNIQUEIDENTIFIER,
name nvarchar(50),
PRIMARY KEY (mixerConditionId)
);

CREATE TABLE tblMixer(
mixerId UNIQUEIDENTIFIER,
mixerConditionId UNIQUEIDENTIFIER,
transportTime decimal(18,2),
rotationSpeed decimal(18,2),
PRIMARY KEY (mixerId),
FOREIGN KEY (mixerConditionId) REFERENCES tblMixerCondition(mixerConditionId)
);

CREATE TABLE tblMixType(
mixtype UNIQUEIDENTIFIER,
name nvarchar(50),
PRIMARY KEY (mixtype)
);

CREATE TABLE tblPlant(
plantId UNIQUEIDENTIFIER,
locationPlant nvarchar(50),
mixingTime decimal(18,2)
PRIMARY KEY (plantId)
);

CREATE TABLE tblConcrete(
concreteId UNIQUEIDENTIFIER,
plantId UNIQUEIDENTIFIER,
buildingId UNIQUEIDENTIFIER,
volume decimal(18,2),
age int,
loadDate datetime,
strength decimal(18,2),
PRIMARY KEY (concreteId),
FOREIGN KEY (plantId) REFERENCES tblPlant(plantId),
FOREIGN KEY (buildingId) REFERENCES tblBuilding(buildingId)
);

CREATE TABLE tblWaterConcrete(
waterConcreteId UNIQUEIDENTIFIER,
quantity decimal(18,2),
pH decimal(18,2),
PRIMARY KEY (waterConcreteId),
);

CREATE TABLE tblCementType(
cementTypeId UNIQUEIDENTIFIER,
name nvarchar(50),
PRIMARY KEY (cementTypeId)
);

CREATE TABLE tblCementComposition(
cementCompositionId UNIQUEIDENTIFIER,
name nvarchar(50),
PRIMARY KEY (cementCompositionId)
);

CREATE TABLE tblCement(
cementId UNIQUEIDENTIFIER,
cementTypeId UNIQUEIDENTIFIER,
cementCompositionId UNIQUEIDENTIFIER,
quantity decimal(18,2),
finesse decimal(18,2),
resistanceUniformity decimal(18,2),
hardeningProperties decimal(18,2),
waterContent decimal(18,2)
PRIMARY KEY (cementId),
FOREIGN KEY (cementTypeId) REFERENCES tblCementType(cementTypeId),
FOREIGN KEY (cementCompositionId) REFERENCES tblCementComposition(cementCompositionId)
);

CREATE TABLE tblCementConcrete(
cementConcreteid UNIQUEIDENTIFIER,
cementId UNIQUEIDENTIFIER,
concreteId UNIQUEIDENTIFIER,
PRIMARY KEY (cementConcreteid),
FOREIGN KEY (cementId) REFERENCES tblCement(cementId),
FOREIGN KEY (concreteId) REFERENCES tblConcrete(concreteId)
);

CREATE TABLE tblAggregatedType(
aggrgatedTypeId UNIQUEIDENTIFIER,
name nvarchar(50),
PRIMARY KEY (aggrgatedTypeId)
);

CREATE TABLE tblAggregatedShape(
aggregatedShapeId UNIQUEIDENTIFIER,
name nvarchar(50),
PRIMARY KEY (aggregatedShapeId)
);

CREATE TABLE tblAggregated(
aggregatedId UNIQUEIDENTIFIER,
aggregatedTypeId UNIQUEIDENTIFIER,
aggregatedShapeId UNIQUEIDENTIFIER,
aggregatedTextureId UNIQUEIDENTIFIER,
quantity decimal(18,2),
moisture decimal(18,2),
hardnees decimal(18,2),
size decimal(18,2),
gradation decimal(18,2),
granulometry decimal(18,2),
Absorption decimal(18,2)
PRIMARY KEY (aggregatedId),
FOREIGN KEY (aggregatedTypeId) REFERENCES tblAggregatedType(aggrgatedTypeId),
FOREIGN KEY (aggregatedShapeId) REFERENCES tblAggregatedShape(aggregatedShapeId)
);

CREATE TABLE tblAggregatedConcrete(
aggregatedConcreteId UNIQUEIDENTIFIER,
aggregatedId UNIQUEIDENTIFIER,
concreteId UNIQUEIDENTIFIER,
PRIMARY KEY (aggregatedConcreteId),
FOREIGN KEY (aggregatedId) REFERENCES tblAggregated(aggregatedId),
FOREIGN KEY (concreteId) REFERENCES tblConcrete(concreteId)
);

CREATE TABLE tblAggregatedTexture(
aggregatedTextureId UNIQUEIDENTIFIER,
name nvarchar(50)
PRIMARY KEY (aggregatedTextureId)
);

CREATE TABLE tblAdditiveType(
additiveTypeId UNIQUEIDENTIFIER,
name nvarchar(50),
PRIMARY KEY (additiveTypeId)
);

CREATE TABLE tblAdditive(
additiveId UNIQUEIDENTIFIER,
additiveTypeId UNIQUEIDENTIFIER,
quantity decimal(18,2),
settingeffect bit,
hardeningeffect bit,
PRIMARY KEY (additiveId),
FOREIGN KEY (additiveTypeId) REFERENCES tblAdditiveType(additiveTypeId),
);

CREATE TABLE tblAdditiveConcrete(
additiveConcrete UNIQUEIDENTIFIER,
additiveId UNIQUEIDENTIFIER,
concreteId UNIQUEIDENTIFIER,
PRIMARY KEY (additiveConcrete),
FOREIGN KEY (additiveId) REFERENCES tblAdditive(additiveId),
FOREIGN KEY (concreteId) REFERENCES tblConcrete(concreteId),
);
