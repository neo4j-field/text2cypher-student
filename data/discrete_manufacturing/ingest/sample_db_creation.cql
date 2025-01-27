
// drop database bodretire;
// create database bodretire;

// **********************************************



// this script to create BOM/BOD database
// used v1.7 intial loading BOM and v1.3 intial loading BOD.

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


// unused
// CREATE INDEX index_HAS_CHILD_for_retrival
// FOR ()-[r:HAS_CHILD]-()
// ON (r.effectivity_date,r.tla_uid,r.disable_date);

// CREATE INDEX index_name_has_child_temp
// FOR ()-[r:HAS_CHILD]-()
// ON (r.effectivity_date,r.tla_uid,r.bill_sequence_id,r.component_sequence_id);


// day 0 metrics node creation(before loading)
CREATE (m:Metrics { job_run_date:datetime() })
 SET m:CurrentMetrics;

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

MATCH (metrics:CurrentMetrics)
WITH line, metrics ,tla_bill_sequence_id

MERGE (c:TLA:FinishedGood {tla_item_uid:line.CHILD_UID+"~"+tla_bill_sequence_id})
 SET 
 c.item_uid=line.CHILD_UID
,c.item_id=toInteger(line.CHILD_ITEM_ID)
,c.organization_id=toInteger(line.ORGANIZATION_ID)
,c.bill_sequence_id=toInteger(tla_bill_sequence_id)
 ,c.organization_code=line.ORGANIZATION_CODE
 ,c.item_number=line.CHILD_ITEM_NUMBER
,c.description=line.CHILD_ITEM_DESCRIPTION
, c.bom_item_type=toInteger(line.CHILD_BOM_ITEM_TYPE)
, c.item_type=line.CHILD_ITEM_TYPE
, c.planning_make_buy_code=toInteger(line.PLANNING_MAKE_BUY_CODE)
, c.inventory_item_status_code=line.INVENTORY_ITEM_STATUS_CODE
, c.UOM_code=line.COMPONENT_UOM
, c.release_phase_code=line.ATTRIBUTE1
, c.model_number=line.ATTRIBUTE2
, c.agency_approval_code=line.ATTRIBUTE3
, c.life_cycle_state=line.ATTRIBUTE4
, c.maximum_order_quantity=toFloat(line.MAXIMUM_ORDER_QUANTITY)
, c.wip_supply_type=toInteger(line.WIP_SUPPLY_TYPE)
, c.wip_supply_type_description=line.SUPPLY_TYPE_DESC
, c.planning_make_buy_code_description=line.PLANNING_MAKE_BUY_CODE_DESCRIPTION
, c.neo4j_last_modified_date=metrics.job_run_date
, c.create_update_indicator="c";




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

MATCH (metrics:CurrentMetrics)
WITH line, metrics

MERGE (c:Item { item_uid:line.CHILD_UID})
 SET 
c.item_id=toInteger(line.CHILD_ITEM_ID)
,c.organization_id=toInteger(line.ORGANIZATION_ID)
 ,c.organization_code=line.ORGANIZATION_CODE
 ,c.item_number=line.CHILD_ITEM_NUMBER
,c.description=line.CHILD_ITEM_DESCRIPTION
, c.bom_item_type=toInteger(line.CHILD_BOM_ITEM_TYPE)
, c.item_type=line.CHILD_ITEM_TYPE
, c.planning_make_buy_code=toInteger(line.PLANNING_MAKE_BUY_CODE)
, c.inventory_item_status_code=line.INVENTORY_ITEM_STATUS_CODE
, c.UOM_code=line.COMPONENT_UOM
, c.release_phase_code=line.ATTRIBUTE1
, c.model_number=line.ATTRIBUTE2
, c.agency_approval_code=line.ATTRIBUTE3
, c.life_cycle_state=line.ATTRIBUTE4
, c.maximum_order_quantity=toFloat(line.MAXIMUM_ORDER_QUANTITY)
, c.wip_supply_type=toInteger(line.WIP_SUPPLY_TYPE)
, c.wip_supply_type_description=line.SUPPLY_TYPE_DESC
, c.planning_make_buy_code_description=line.PLANNING_MAKE_BUY_CODE_DESCRIPTION
, c.neo4j_last_modified_date=metrics.job_run_date
, c.create_update_indicator="c";


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

MATCH (metrics:CurrentMetrics)
WITH line, metrics

// parent item retrival // parent could be TLA which need to be identified by tla_item_uid

MATCH (p:Item|TLA{item_uid:line.PARENT_UID})

WITH line,metrics,  p
// child item retrival
MATCH (c:Item { item_uid:line.CHILD_UID})
WITH line,metrics,p,c

// creation of hierarchy
MERGE (c)<-[r:HAS_CHILD {effectivity_date:datetime(line.EFFECTIVITY_DATE),bill_sequence_id:toInteger(line.PARENT_BILL_SEQUENCE_ID),tla_uid:line.TLA_UID,component_sequence_id:toInteger(line.COMPONENT_SEQUENCE_ID)}]-(p)
 SET 
 r.item_num=toInteger(line.ITEM_NUM)
, r.implementation_date=datetime(line.IMPLEMENTATION_DATE)
, r.operation_seq_num=toInteger(line.OPERATION_SEQ_NUM)
, r.component_quantity=toFloat(line.COMPONENT_QUANTITY)
, r.component_uom=line.COMPONENT_UOM
, r.disable_date=datetime(line.DISABLE_DATE)
, r.neo4j_last_modified_date=metrics.job_run_date
, r.create_update_indicator="c";


//***********************************
// Step#5 refactoring
//***********************************
// #### BOM explosion
//  Mapping a node as stopping node for BOM explosion

CALL apoc.periodic.iterate(
"
MATCH (a:Item)
WHERE a.item_type='PBOM' OR a.bom_item_type=1 OR a.bom_item_type=2 OR a.planning_make_buy_code=2 AND NOT a:StopBOMExplosion
RETURN a;", " SET a:StopBOMExplosion;",
{ batchSize:10000, parallel: true , retries:3, concurrency:50 }) YIELD batches, total , timeTaken , committedOperations , failedOperations, failedBatches , retries , errorMessages , batch , operations , wasTerminated , failedParams
RETURN *;

// set the lable for Finished Good

CALL apoc.periodic.iterate(
'
MATCH (a:Item)
WHERE a.item_type="CTO" or a.item_type="ETO-SERIAL" or a.item_type="PRECONFIG-MAKE" or a.item_type="SO" AND NOT a:FinishedGood
RETURN a;', " SET a:FinishedGood;",
{ batchSize:10000, parallel: true , retries:3, concurrency:50 }) YIELD batches, total , timeTaken , committedOperations , failedOperations, failedBatches , retries , errorMessages , batch , operations , wasTerminated , failedParams
RETURN *;

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

// set the lable of leaf
CALL apoc.periodic.iterate(
"
MATCH (a:Item)
WHERE NOT (a)-[:HAS_CHILD]->() AND NOT a:Leaf
RETURN a;", " SET a:Leaf;",
{ batchSize:10000, parallel: true , retries:3, concurrency:50 }) YIELD batches, total , timeTaken , committedOperations , failedOperations, failedBatches , retries , errorMessages , batch , operations , wasTerminated , failedParams
RETURN *;

//***********************************
// Step#6 Updating the metrics for the job run
//***********************************
// Storing meta stats at the end of the program

Call apoc.meta.stats()
yield labels, relTypesCount, labelCount, relTypeCount, propertyKeyCount, nodeCount, relCount
MATCH (a:CurrentMetrics)
 SET a.labelCount=labelCount
, a.relTypeCount=relTypeCount
, a.propertyKeyCount=propertyKeyCount
, a.nodeCount=nodeCount
, a.relCount=relCount
, a.labels=apoc.text.toCypher(labels)
, a.relTypesCount=apoc.text.toCypher(relTypesCount);

// Counts for initial load
MATCH (a:CurrentMetrics)
MATCH (i:Item{ neo4j_last_modified_date:a.job_run_date })
WITH a,labels(i) AS lables, i.neo4j_last_modified_date AS neo4j_last_modified_date, i.create_update_indicator AS create_update_indicator
WITH a,lables, neo4j_last_modified_date, create_update_indicator, count(*) AS counts
// making collection of the metrics
WITH a,collect(apoc.text.toCypher({labels:lables, neo4j_last_modified_date:toString(neo4j_last_modified_date), create_update_indicator:create_update_indicator, counts:counts })) AS node_counts
SET a.node_counts_current_run_only=node_counts;

// // counts for relations
MATCH (a:CurrentMetrics)
MATCH ()-[i:HAS_CHILD{ neo4j_last_modified_date:a.job_run_date }]->()
// USING INDEX i:HAS_CHILD(neo4j_last_modified_date)
WITH a,type(i) AS relation_type, i.neo4j_last_modified_date AS neo4j_last_modified_date, i.create_update_indicator AS create_update_indicator
WITH a,relation_type, neo4j_last_modified_date, create_update_indicator, count(*) AS counts
// making collection of the metrics
WITH a,collect(apoc.text.toCypher({relation_type:relation_type, neo4j_last_modified_date:toString(neo4j_last_modified_date), create_update_indicator:create_update_indicator, counts:counts })) AS rel_counts
SET a.relationships_counts_current_run_only=rel_counts;

// updating the last run details from the perspective of fact table
// SQl for the current fact table data information
LOAD CSV
WITH HEADERS FROM
'file:///bom_bod_sample.csv'
 AS line
 WITH count(*) AS total_lines_count, collect(line) AS lines
 WITH total_lines_count,lines[0].ROW_ID AS first_row_id,lines[-1].ROW_ID AS last_row_id,lines[0].ROW_CREATION_DT AS first_row_creation_date,lines[-1].ROW_CREATION_DT AS last_row_creation_date
 // sql end 
 MATCH (a:CurrentMetrics)
SET a.fact_table_details = apoc.text.toCypher({total_lines_count: total_lines_count,first_row_id_for_current_run:first_row_id,last_row_id_for_current_run:last_row_id,
first_row_creation_date:first_row_creation_date,last_row_creation_date:last_row_creation_date});


// VERSION HISTORY
// V1.1
// 1.Separating the suppier node creation.
// 2. added the metrics related data
// v 1.2 
// 1. separating logic for COST node too for count queries
// v1.3 
// index was missing on the HAS_COST and HAS_SUPPLIER
// About metrics node
// we are creating a new metrics node for BOD and update all the node counts


// Creating the metrics node for BOD
MATCH (a:CurrentMetrics)
CREATE (b:Metrics { job_run_date:datetime() })
 SET b:CurrentMetrics
MERGE (a)-[:NEXT]->(b)
REMOVE a:CurrentMetrics;

// Constraints and indexs
CREATE CONSTRAINT constraint_Supplier_name_id_country IF NOT EXISTS
FOR (p:Supplier)
REQUIRE (p.supplier_name,p.vendor_site_code,p.country) IS UNIQUE;


CREATE CONSTRAINT constraint_cost_id IF NOT EXISTS
FOR (c:Cost)
REQUIRE (c.item_uid,c.cost_type) IS UNIQUE;

CREATE RANGE INDEX index_HAS_COST_neo4j_last_modified_date
FOR ()-[k:HAS_COST]-() ON (k.neo4j_last_modified_date);

CREATE RANGE INDEX index_HAS_SUPPLIER_neo4j_last_modified_date
FOR ()-[k:HAS_SUPPLIER]-() ON (k.neo4j_last_modified_date);


// ************  SUPPLIER ***********
// take only non null SUPPLIER_NAME rows

// Supplier node creation
LOAD CSV
WITH HEADERS FROM
'file:///bom_bod_sample.csv'
 AS line
WITH line WHERE line.SUPPLIER_NAME IS NOT NULL AND line.VENDOR_SITE_CODE IS NOT NULL AND line.COUNTRY IS NOT NULL
MATCH (metrics:CurrentMetrics)
MERGE (s:Supplier {supplier_name:line.SUPPLIER_NAME,vendor_site_code:line.VENDOR_SITE_CODE,country:line.COUNTRY})
set s.neo4j_last_modified_date=metrics.job_run_date;
// these two fields are coming from items. So excluding here.
//,s.wip_supply_type=line.WIP_SUPPLY_TYPE
// ,s.supplye_type_desc=line.SUPPLY_TYPE_DESC



// HAS_SUPPLIER relation creation
LOAD CSV
WITH HEADERS FROM
'file:///bom_bod_sample.csv'
 AS line
WITH line WHERE line.SUPPLIER_NAME IS NOT NULL AND line.VENDOR_SITE_CODE IS NOT NULL AND line.COUNTRY IS NOT NULL
MATCH (metrics:CurrentMetrics)
MATCH (a:Item|TLA {item_uid:line.CHILD_UID})
MATCH (s:Supplier {supplier_name:line.SUPPLIER_NAME,vendor_site_code:line.VENDOR_SITE_CODE,country:line.COUNTRY})
MERGE (a)-[r:HAS_SUPPLIER]->(s)
SET r.neo4j_last_modified_date=metrics.job_run_date;
// these two fileds are excluded for time being as there are duplicates seen for this field
// ,r.unit_price=line.UNIT_PRICE
// ,r.currency_code=line.CURRENCY_CODE


// Roni: supplier is a dense node. please run 1 job and no parallel.
// ravi: Supplier will be separate logic then create the relations. - done

// ************  COST ***********
//Keep the cost key as child_uid and the cost_type
LOAD CSV
WITH HEADERS FROM
'file:///bom_bod_sample.csv'
 AS line
WITH line WHERE line.CHILD_UID IS NOT NULL AND line.COST_TYPE IS NOT NULL
MATCH (metrics:CurrentMetrics)
MATCH (a:Item|TLA  {item_uid:line.CHILD_UID})
MERGE (c:Cost {item_uid:line.CHILD_UID,cost_type:line.COST_TYPE})
set c.cost_type_description=line.COST_TYPE_DESCRIPTION
 ,c.cost_type_name=line.COST_TYPE_NAME
 ,c.year=toInteger(line.YEAR)
 ,c.time_period=line.TIME_PERIOD
 ,c.item_cost=toFloat(line.ITEM_COST)
 ,c.material_cost=toFloat(line.MATERIAL_COST)
 ,c.material_overhead_cost=toFloat(line.MATERIAL_OVERHEAD_COST)
 ,c.resource_cost=toFloat(line.RESOURCE_COST)
 ,c.outside_processing_cost=toFloat(line.OUTSIDE_PROCESSING_COST)
 ,c.overhaead_cost=toFloat(line.OVERHEAD_COST)
 ,c.neo4j_last_modified_date=metrics.job_run_date;


// HAS_COST CREATION 
LOAD CSV
WITH HEADERS FROM
'file:///bom_bod_sample.csv'
 AS line
WITH line WHERE line.CHILD_UID IS NOT NULL AND line.COST_TYPE IS NOT NULL
MATCH (metrics:CurrentMetrics)
MATCH (a:Item|TLA  {item_uid:line.CHILD_UID})
MATCH (c:Cost {item_uid:line.CHILD_UID,cost_type:line.COST_TYPE})
MERGE (a)-[r:HAS_COST]->(c)
SET r.neo4j_last_modified_date=metrics.job_run_date;

// 
// Reactive cost 
// Historical data - 2 years max 
// Frozen cost 
// Historical data - 5 years

// estimated at the most 14 cost records will be there for each item. reactive costs 2 year * 4 quaters + Frozen cost 5+1 (next year) 
// Cost is not a dense node. 


 

//***********************************
// Updating the metrics for the job run
//***********************************
// Storing meta stats at the end of the program

Call apoc.meta.stats()
yield labels, relTypesCount, labelCount, relTypeCount, propertyKeyCount, nodeCount, relCount
MATCH (a:CurrentMetrics)
 SET a.labelCount=labelCount
, a.relTypeCount=relTypeCount
, a.propertyKeyCount=propertyKeyCount
, a.nodeCount=nodeCount
, a.relCount=relCount
, a.labels=apoc.text.toCypher(labels)
, a.relTypesCount=apoc.text.toCypher(relTypesCount);

// Counts for incremental load
MATCH (a:CurrentMetrics)
MATCH (i:Item{ neo4j_last_modified_date:a.job_run_date })
WITH a,labels(i) AS lables, i.neo4j_last_modified_date AS neo4j_last_modified_date, i.create_update_indicator AS create_update_indicator
WITH a,lables, neo4j_last_modified_date, create_update_indicator, count(*) AS counts
WITH a,collect(apoc.text.toCypher({labels:lables, neo4j_last_modified_date:toString(neo4j_last_modified_date), create_update_indicator:create_update_indicator, counts:counts })) AS node_counts
SET a.node_counts_current_run_only=node_counts;

// // counts for relations
MATCH (a:CurrentMetrics)
MATCH ()-[i:HAS_COST|HAS_SUPPLIER{ neo4j_last_modified_date:a.job_run_date }]->()
// USING INDEX i:HAS_CHILD(neo4j_last_modified_date)
WITH a,type(i) AS relation_type, i.neo4j_last_modified_date AS neo4j_last_modified_date, i.create_update_indicator AS create_update_indicator
WITH a,relation_type, neo4j_last_modified_date, create_update_indicator, count(*) AS counts
WITH a,collect(apoc.text.toCypher({relation_type:relation_type, neo4j_last_modified_date:toString(neo4j_last_modified_date), create_update_indicator:create_update_indicator, counts:counts })) AS rel_counts
SET a.relationships_counts_current_run_only=rel_counts;

// updating the last run details from the perspective of fact table
// SQl for the current fact table data information
LOAD CSV
WITH HEADERS FROM
'file:///bom_bod_sample.csv'
 AS line
 WITH count(*) AS total_lines_count, collect(line) AS lines
 WITH total_lines_count,lines[0].ROW_ID AS first_row_id,lines[-1].ROW_ID AS last_row_id,lines[0].ROW_CREATION_DT AS first_row_creation_date,lines[-1].ROW_CREATION_DT AS last_row_creation_date
 // sql end 
 MATCH (a:CurrentMetrics)
SET a.fact_table_details = apoc.text.toCypher({total_lines_count: total_lines_count,first_row_id_for_current_run:first_row_id,last_row_id_for_current_run:last_row_id,
first_row_creation_date:first_row_creation_date,last_row_creation_date:last_row_creation_date});


