
# <a id='_modelTop'></a>Honda IQS Neo4j Data Model

**Date:** Fri Jul 12 2024
**Solutions Workbench Version:** 1.5.1
**Description:** Neo4j knowledge graph model that represents the 2023 IQS data
**Stats:**  6 node labels, 8 relationship types,
22 node label properties, 0 relationship type properties

<img src="../images/graph-model.png" width="630">

### Table of Contents

#### Node Labels
* [Category](#Node2)
* [Customer](#Node0)
* [Problem](#Node3)
* [Question](#Node5)
* [Vehicle](#Node19)
* [Verbatim](#Node7)

#### Relationship Types
* [HAS_CATEGORY](#Rel28)
* [HAS_CATEGORY](#Rel22)
* [HAS_CATEGORY](#Rel25)
* [HAS_PROBLEM](#Rel26)
* [HAS_PROBLEM](#Rel23)
* [HAS_QUESTION](#Rel24)
* [HAS_VERBATIM](#Rel27)
* [SUBMITTED](#Rel21)

## Node Labels
--------------

### <a id='Node2'></a>Category <span style="font-size:0.7em;">[[top]](#_modelTop)</span>
---

#### Category Inbound Relationships

[Vehicle](#Node19) - [HAS_CATEGORY](#Rel28) -> Category
[Problem](#Node3) - [HAS_CATEGORY](#Rel22) -> Category
[Verbatim](#Node7) - [HAS_CATEGORY](#Rel25) -> Category

#### Category Properties

Node Key: id
Unique Constraint Properties: id
Indexed Properties: id
Must Exist Properties: id

**id**
Datatype: String
Node Key, Unique Constraint, Indexed, Must Exist

### <a id='Node0'></a>Customer <span style="font-size:0.7em;">[[top]](#_modelTop)</span>
---

#### Customer Outbound Relationships

Customer - [SUBMITTED](#Rel21) -> [Verbatim](#Node7)

#### Customer Properties

Node Key: id
Unique Constraint Properties: id
Indexed Properties: id
Must Exist Properties: id

**ageBucket**
Datatype: String

**gender**
Datatype: String

**id**
Datatype: String
Node Key, Unique Constraint, Indexed, Must Exist

### <a id='Node3'></a>Problem <span style="font-size:0.7em;">[[top]](#_modelTop)</span>
---

#### Problem Outbound Relationships

Problem - [HAS_CATEGORY](#Rel22) -> [Category](#Node2)

#### Problem Inbound Relationships

[Verbatim](#Node7) - [HAS_PROBLEM](#Rel26) -> Problem
[Question](#Node5) - [HAS_PROBLEM](#Rel23) -> Problem

#### Problem Properties

Unique Constraint Properties: id
Indexed Properties: id

**id**
Datatype: String
Unique Constraint, Indexed

**problem**
Datatype: String

### <a id='Node5'></a>Question <span style="font-size:0.7em;">[[top]](#_modelTop)</span>
---

#### Question Outbound Relationships

Question - [HAS_PROBLEM](#Rel23) -> [Problem](#Node3)

#### Question Inbound Relationships

[Verbatim](#Node7) - [HAS_QUESTION](#Rel24) -> Question

#### Question Properties

Node Key: id
Unique Constraint Properties: id
Indexed Properties: id
Must Exist Properties: id

**id**
Datatype: Integer
Node Key, Unique Constraint, Indexed, Must Exist

**question**
Datatype: String

### <a id='Node19'></a>Vehicle <span style="font-size:0.7em;">[[top]](#_modelTop)</span>
---

#### Vehicle Outbound Relationships

Vehicle - [HAS_CATEGORY](#Rel28) -> [Category](#Node2)
Vehicle - [HAS_VERBATIM](#Rel27) -> [Verbatim](#Node7)

#### Vehicle Properties

Node Key: id
Unique Constraint Properties: id
Indexed Properties: id
Must Exist Properties: id

**id**
Datatype: String
Node Key, Unique Constraint, Indexed, Must Exist

**totalProblems**
Datatype: Integer

### <a id='Node7'></a>Verbatim <span style="font-size:0.7em;">[[top]](#_modelTop)</span>
---

#### Verbatim Outbound Relationships

Verbatim - [HAS_CATEGORY](#Rel25) -> [Category](#Node2)
Verbatim - [HAS_PROBLEM](#Rel26) -> [Problem](#Node3)
Verbatim - [HAS_QUESTION](#Rel24) -> [Question](#Node5)

#### Verbatim Inbound Relationships

[Vehicle](#Node19) - [HAS_VERBATIM](#Rel27) -> Verbatim
[Customer](#Node0) - [SUBMITTED](#Rel21) -> Verbatim

#### Verbatim Properties

Node Key: id, verbatim
Unique Constraint Properties: id, verbatim
Indexed Properties: id, verbatim, verbatimText
Must Exist Properties: id, verbatim

**adaEmbedding**
Datatype: List<Float>

**ageBucket**
Datatype: String

**gender**
Datatype: String

**id**
Datatype: String
Node Key, Unique Constraint, Indexed, Must Exist

**make**
Datatype: String

**maxAge**
Datatype: Integer

**minAge**
Datatype: Integer

**model**
Datatype: String

**severity**
Datatype: Float

**titanEmbedding**
Datatype: List<Float>

**verbatim**
Datatype: String
Node Key, Unique Constraint, Indexed, Must Exist

**verbatimText**
Datatype: String
Indexed

## Relationship Types
--------------

### <a id='Rel28'></a>HAS_CATEGORY <span style="font-size:0.7em;">[[top]](#_modelTop)</span>
---
[Vehicle](#Node19) - HAS_CATEGORY -> [Category](#Node2)

### <a id='Rel22'></a>HAS_CATEGORY <span style="font-size:0.7em;">[[top]](#_modelTop)</span>
---
[Problem](#Node3) - HAS_CATEGORY -> [Category](#Node2)

### <a id='Rel25'></a>HAS_CATEGORY <span style="font-size:0.7em;">[[top]](#_modelTop)</span>
---
[Verbatim](#Node7) - HAS_CATEGORY -> [Category](#Node2)

### <a id='Rel26'></a>HAS_PROBLEM <span style="font-size:0.7em;">[[top]](#_modelTop)</span>
---
[Verbatim](#Node7) - HAS_PROBLEM -> [Problem](#Node3)

### <a id='Rel23'></a>HAS_PROBLEM <span style="font-size:0.7em;">[[top]](#_modelTop)</span>
---
[Question](#Node5) - HAS_PROBLEM -> [Problem](#Node3)

### <a id='Rel24'></a>HAS_QUESTION <span style="font-size:0.7em;">[[top]](#_modelTop)</span>
---
[Verbatim](#Node7) - HAS_QUESTION -> [Question](#Node5)

### <a id='Rel27'></a>HAS_VERBATIM <span style="font-size:0.7em;">[[top]](#_modelTop)</span>
---
[Vehicle](#Node19) - HAS_VERBATIM -> [Verbatim](#Node7)

### <a id='Rel21'></a>SUBMITTED <span style="font-size:0.7em;">[[top]](#_modelTop)</span>
---
[Customer](#Node0) - SUBMITTED -> [Verbatim](#Node7)
