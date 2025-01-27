
// TLA
CREATE CONSTRAINT constraint_TLA_item_uid IF NOT EXISTS
FOR (p:TLA)
REQUIRE (p.tla_item_uid) IS UNIQUE;

CREATE INDEX index_TLA_bill_sequence_id IF NOT EXISTS
FOR (p:TLA) ON (p.bill_sequence_id);

CREATE INDEX index_TLA_item_number IF NOT EXISTS
FOR (p:TLA) ON (p.item_number);

CREATE INDEX index_TLA_item_uid IF NOT EXISTS
FOR (p:TLA) ON (p.item_uid);

CREATE INDEX index_TLA_item_id IF NOT EXISTS
FOR (p:TLA) ON (p.item_id);

CREATE INDEX index_TLA_ietm_id_org_id IF NOT EXISTS
FOR (p:TLA)
ON (p.organization_id, p.item_id);

// Item

CREATE CONSTRAINT constraint_ITEM_item_uid IF NOT EXISTS
FOR (p:Item)
REQUIRE (p.item_uid) IS UNIQUE;

CREATE INDEX index_item_number IF NOT EXISTS
FOR (p:Item) ON (p.item_number);

CREATE INDEX index_item_id IF NOT EXISTS
FOR (p:Item) ON (p.item_id);

CREATE INDEX index_neo4j_last_modified_date IF NOT EXISTS
FOR (p:Item) ON (p.neo4j_last_modified_date);

CREATE INDEX index_item_ietm_id_org_id IF NOT EXISTS
FOR (p:Item)
ON (p.organization_id, p.item_id);

// HAS_CHILD
CREATE CONSTRAINT constraint_name_has_child IF NOT EXISTS
FOR ()-[r:HAS_CHILD]-()
REQUIRE (r.effectivity_date,r.tla_uid,r.bill_sequence_id,r.component_sequence_id) IS UNIQUE;

CREATE RANGE INDEX index_HAS_CHILD_neo4j_last_modified_date IF NOT EXISTS
FOR ()-[k:HAS_CHILD]-() ON (k.neo4j_last_modified_date);

CREATE RANGE INDEX index_HAS_CHILD_tla_uid IF NOT EXISTS
FOR ()-[k:HAS_CHILD]-() ON (k.tla_uid);


//***********************************
// Step#2 process for TLA node creation
//***********************************

// sql part start
LOAD CSV
WITH HEADERS FROM
'file:///bom_bod_sample.csv'
 AS line
  WITH line WHERE line.TLA_UID='TLA' or line.TLA_UID IS NULL

WITH line,line.CHILD_ITEM_ID AS tla_id,line.bill_sequence_id AS on_tla_BSI 

CALL (tla_id) {WITH tla_id
LOAD CSV
WITH HEADERS FROM
'file:///bom_bod_sample.csv'
 AS header_line
  WITH header_line WHERE 
  
NOT (header_line.TLA_UID='TLA' or header_line.TLA_UID IS NULL) AND 
header_line.PARENT_ITEM_ID=tla_id
  RETURN DISTINCT header_line.PARENT_BILL_SEQUENCE_ID AS tla_bill_sequence_id
}
WITH line, tla_bill_sequence_id
          
// sql part end

WITH line ,tla_bill_sequence_id

MERGE (c:TLA:FinishedGood {tla_item_uid:line.CHILD_UID+"~"+tla_bill_sequence_id})
 SET 
 c.item_uid=line.CHILD_UID
,c.item_id=toInteger(line.CHILD_ITEM_ID)
,c.organization_id=toInteger(line.ORGANIZATION_ID)
,c.bill_sequence_id=toInteger(tla_bill_sequence_id)
 ,c.organization_code=line.ORGANIZATION_CODE
,c.description=line.CHILD_ITEM_DESCRIPTION
, c.bom_item_type=toInteger(line.CHILD_BOM_ITEM_TYPE)
, c.item_type=line.CHILD_ITEM_TYPE
, c.planning_make_buy_code=toInteger(line.PLANNING_MAKE_BUY_CODE)
, c.UOM_code=line.COMPONENT_UOM
, c.maximum_order_quantity=toFloat(line.MAXIMUM_ORDER_QUANTITY)
, c.planning_make_buy_code_description=line.PLANNING_MAKE_BUY_CODE_DESCRIPTION;




//***********************************
// Step#3 load the component Items
//***********************************
// sql part start
LOAD CSV
WITH HEADERS FROM
'file:///bom_bod_sample.csv'
 AS line
WITH line WHERE line.TLA_UID<>'TLA' AND line.TLA_UID IS NOT NULL

// sql part end

WITH line

MERGE (c:Item { item_uid:line.CHILD_UID})
 SET 
c.item_id=toInteger(line.CHILD_ITEM_ID)
,c.organization_id=toInteger(line.ORGANIZATION_ID)
 ,c.organization_code=line.ORGANIZATION_CODE
,c.description=line.CHILD_ITEM_DESCRIPTION
, c.bom_item_type=toInteger(line.CHILD_BOM_ITEM_TYPE)
, c.item_type=line.CHILD_ITEM_TYPE
, c.planning_make_buy_code=toInteger(line.PLANNING_MAKE_BUY_CODE)
, c.UOM_code=line.COMPONENT_UOM
, c.maximum_order_quantity=toFloat(line.MAXIMUM_ORDER_QUANTITY)
, c.planning_make_buy_code_description=line.PLANNING_MAKE_BUY_CODE_DESCRIPTION;


//***********************************
// Step#4 load the relations
//***********************************


// sql part start
LOAD CSV
WITH HEADERS FROM
'file:///bom_bod_sample.csv'
 AS line
WITH line WHERE line.TLA_UID<>'TLA' AND line.TLA_UID IS NOT NULL

// sql part end

WITH line

// parent item retrival // parent could be TLA which need to be identified by tla_item_uid

MATCH (p:Item|TLA{item_uid:line.PARENT_UID})

WITH line,  p
// child item retrival
MATCH (c:Item { item_uid:line.CHILD_UID})
WITH line,p,c

// creation of hierarchy
MERGE (c)<-[r:HAS_CHILD {effectivity_date:datetime(line.EFFECTIVITY_DATE),bill_sequence_id:toInteger(line.PARENT_BILL_SEQUENCE_ID),tla_uid:line.TLA_UID,component_sequence_id:toInteger(line.COMPONENT_SEQUENCE_ID)}]-(p)
 SET 
r.implementation_date=datetime(line.IMPLEMENTATION_DATE)
, r.component_quantity=toFloat(line.COMPONENT_QUANTITY)
, r.component_uom=line.COMPONENT_UOM
, r.disable_date=datetime(line.DISABLE_DATE);


//***********************************
// Step#5 refactoring
//***********************************


// model setting for items
CALL apoc.periodic.iterate(
'
MATCH (a:TLA)-[r:HAS_CHILD]->(b)  WHERE b.bom_item_type=1
RETURN a,b,r;', 
" SET b:Model:StopBOMExplosion
SET a.model_id=b.item_number;",
{ batchSize:10000, parallel: true , retries:3, concurrency:50 }) YIELD batches, total , timeTaken , committedOperations , failedOperations, failedBatches , retries , errorMessages , batch , operations , wasTerminated , failedParams
RETURN *;

// Option setting for items
CALL apoc.periodic.iterate(
'
MATCH (a:TLA)-[r:HAS_CHILD]->(b)  WHERE b.bom_item_type=2
RETURN a,b,r;', 
" SET b:Option:StopBOMExplosion;",
{ batchSize:10000, parallel: true , retries:3, concurrency:50 }) YIELD batches, total , timeTaken , committedOperations , failedOperations, failedBatches , retries , errorMessages , batch , operations , wasTerminated , failedParams
RETURN *;



// *******************************   BOD  *******************************
// **************************************************************


// Constraints and indexs
CREATE CONSTRAINT constraint_Supplier_name_id_country IF NOT EXISTS
FOR (p:Supplier)
REQUIRE (p.supplier_name,p.vendor_site_code,p.country) IS UNIQUE;


CREATE CONSTRAINT constraint_cost_id IF NOT EXISTS
FOR (c:Cost)
REQUIRE (c.item_uid,c.cost_type) IS UNIQUE;

CREATE RANGE INDEX index_HAS_COST_neo4j_last_modified_date IF NOT EXISTS
FOR ()-[k:HAS_COST]-() ON (k.neo4j_last_modified_date);

CREATE RANGE INDEX index_HAS_SUPPLIER_neo4j_last_modified_date IF NOT EXISTS
FOR ()-[k:HAS_SUPPLIER]-() ON (k.neo4j_last_modified_date);


// ************  SUPPLIER ***********
// take only non null SUPPLIER_NAME rows

// Supplier node creation
LOAD CSV
WITH HEADERS FROM
'file:///bom_bod_sample.csv'
 AS line
WITH line WHERE line.SUPPLIER_NAME IS NOT NULL AND line.VENDOR_SITE_CODE IS NOT NULL AND line.COUNTRY IS NOT NULL
MERGE (s:Supplier {supplier_name:line.SUPPLIER_NAME,vendor_site_code:line.VENDOR_SITE_CODE,country:line.COUNTRY});




// HAS_SUPPLIER relation creation
LOAD CSV
WITH HEADERS FROM
'file:///bom_bod_sample.csv'
 AS line
WITH line WHERE line.SUPPLIER_NAME IS NOT NULL AND line.VENDOR_SITE_CODE IS NOT NULL AND line.COUNTRY IS NOT NULL
MATCH (a:Item|TLA {item_uid:line.CHILD_UID})
MATCH (s:Supplier {supplier_name:line.SUPPLIER_NAME,vendor_site_code:line.VENDOR_SITE_CODE,country:line.COUNTRY})
MERGE (a)-[r:HAS_SUPPLIER]->(s);




// Roni: supplier is a dense node. please run 1 job and no parallel.
// ravi: Supplier will be separate logic then create the relations. - done

// ************  COST ***********
//Keep the cost key as child_uid and the cost_type
LOAD CSV
WITH HEADERS FROM
'file:///bom_bod_sample.csv'
 AS line
WITH line WHERE line.CHILD_UID IS NOT NULL AND line.COST_TYPE IS NOT NULL
MATCH (a:Item|TLA  {item_uid:line.CHILD_UID})
MERGE (c:Cost {item_uid:line.CHILD_UID,cost_type:line.COST_TYPE})
set c.cost_type_description=line.COST_TYPE_DESCRIPTION
 ,c.cost_type_name=line.COST_TYPE_NAME
 ,c.year=toInteger(line.YEAR)
 ,c.time_period=line.TIME_PERIOD
 ,c.item_cost=toFloat(line.ITEM_COST)
 ,c.material_cost=toFloat(line.MATERIAL_COST)
 ,c.resource_cost=toFloat(line.RESOURCE_COST);



// HAS_COST CREATION 
LOAD CSV
WITH HEADERS FROM
'file:///bom_bod_sample.csv'
 AS line
WITH line WHERE line.CHILD_UID IS NOT NULL AND line.COST_TYPE IS NOT NULL
MATCH (a:Item|TLA  {item_uid:line.CHILD_UID})
MATCH (c:Cost {item_uid:line.CHILD_UID,cost_type:line.COST_TYPE})
MERGE (a)-[r:HAS_COST]->(c);

 
