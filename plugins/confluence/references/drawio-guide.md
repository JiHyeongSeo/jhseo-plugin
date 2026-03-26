# draw.io 다이어그램 Best Practice 가이드

draw.io 다이어그램 작성 시 유형별 Shape, 색상, 레이아웃 가이드입니다.
기본 draw.io XML 포맷 및 Confluence 삽입 방법은 `style-guide.md` 섹션 22-23을 참고하세요.

## 공통 색상 원칙

파스텔톤을 사용합니다. 한 다이어그램에 3-4색 이내로 제한합니다.

| 역할 | fillColor | strokeColor | 용도 |
|------|-----------|-------------|------|
| **기본 (파랑)** | `#dae8fc` | `#6c8ebf` | 내부 서비스, 일반 노드 |
| **보조 (회색)** | `#f5f5f5` | `#999999` | 배경, 레이어, 보조 요소 |
| **강조 (노랑)** | `#fff2cc` | `#d6b656` | 판단, 게이트웨이, 외부 서비스 |
| **경고 (빨강)** | `#f8cecc` | `#b85450` | 방화벽, DMZ, 주의 요소 |
| **성공 (초록)** | `#d5e8d4` | `#82b366` | 완료, 입출력, 정상 상태 |
| **보라** | `#e1d5e7` | `#9673a6` | DB/저장소, 서브프로세스 |
| **비활성** | `#f5f5f5` | `#666666` | 비활성, 미정, 선택사항 |
| **텍스트** | - | `#666666` | 화살표, 일반 선 |
| **강조 텍스트** | - | `#333333` | 종료 이벤트, 초기 상태 |

## 1. ERD (Entity Relationship Diagram)

**용도:** DB 테이블 구조와 관계를 시각화할 때

**Entity 스타일:**
```xml
<!-- Entity 테이블 (컨테이너) -->
<mxCell id="entity1" value="users" style="shape=table;startSize=30;container=1;collapsible=0;childLayout=tableLayout;fixedRows=1;rowLines=0;fontStyle=1;align=center;resizeLast=1;html=1;fillColor=#f5f5f5;strokeColor=#666666;strokeWidth=2;fontSize=13;" vertex="1" parent="1">
  <mxGeometry x="40" y="40" width="220" height="120" as="geometry"/>
</mxCell>

<!-- 테이블 행 (TR) -->
<mxCell id="row1" value="" style="shape=tableRow;horizontal=0;startSize=0;swimlaneHead=0;swimlaneBody=0;fillColor=none;collapsible=0;dropTarget=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;fontSize=12;top=0;left=0;right=0;bottom=0;" vertex="1" parent="entity1">
  <mxGeometry y="30" width="220" height="30" as="geometry"/>
</mxCell>

<!-- PK 컬럼 (아이콘 셀) -->
<mxCell id="pk_icon" value="PK" style="shape=partialRectangle;connectable=0;fillColor=none;top=0;left=0;bottom=0;right=0;fontStyle=1;overflow=hidden;fontSize=11;fontColor=#cc0000;" vertex="1" parent="row1">
  <mxGeometry width="40" height="30" as="geometry">
    <mxRectangle width="40" height="30" as="alternateBounds"/>
  </mxGeometry>
</mxCell>

<!-- PK 컬럼명 셀 -->
<mxCell id="pk_name" value="id INT" style="shape=partialRectangle;connectable=0;fillColor=none;top=0;left=0;bottom=0;right=0;overflow=hidden;fontSize=12;fontStyle=1;" vertex="1" parent="row1">
  <mxGeometry x="40" width="180" height="30" as="geometry">
    <mxRectangle width="180" height="30" as="alternateBounds"/>
  </mxGeometry>
</mxCell>

<!-- 일반 컬럼 행 -->
<mxCell id="row2" value="" style="shape=tableRow;horizontal=0;startSize=0;swimlaneHead=0;swimlaneBody=0;fillColor=none;collapsible=0;dropTarget=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;fontSize=12;top=0;left=0;right=0;bottom=0;" vertex="1" parent="entity1">
  <mxGeometry y="60" width="220" height="30" as="geometry"/>
</mxCell>
<mxCell id="col_icon" value="" style="shape=partialRectangle;connectable=0;fillColor=none;top=0;left=0;bottom=0;right=0;overflow=hidden;fontSize=11;" vertex="1" parent="row2">
  <mxGeometry width="40" height="30" as="geometry">
    <mxRectangle width="40" height="30" as="alternateBounds"/>
  </mxGeometry>
</mxCell>
<mxCell id="col_name" value="name VARCHAR(100)" style="shape=partialRectangle;connectable=0;fillColor=none;top=0;left=0;bottom=0;right=0;overflow=hidden;fontSize=12;" vertex="1" parent="row2">
  <mxGeometry x="40" width="180" height="30" as="geometry">
    <mxRectangle width="180" height="30" as="alternateBounds"/>
  </mxGeometry>
</mxCell>

<!-- FK 컬럼 행 -->
<mxCell id="row3" value="" style="shape=tableRow;horizontal=0;startSize=0;swimlaneHead=0;swimlaneBody=0;fillColor=none;collapsible=0;dropTarget=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;fontSize=12;top=0;left=0;right=0;bottom=0;" vertex="1" parent="entity1">
  <mxGeometry y="90" width="220" height="30" as="geometry"/>
</mxCell>
<mxCell id="fk_icon" value="FK" style="shape=partialRectangle;connectable=0;fillColor=none;top=0;left=0;bottom=0;right=0;fontStyle=1;overflow=hidden;fontSize=11;fontColor=#336699;" vertex="1" parent="row3">
  <mxGeometry width="40" height="30" as="geometry">
    <mxRectangle width="40" height="30" as="alternateBounds"/>
  </mxGeometry>
</mxCell>
<mxCell id="fk_name" value="team_id INT" style="shape=partialRectangle;connectable=0;fillColor=none;top=0;left=0;bottom=0;right=0;overflow=hidden;fontSize=12;" vertex="1" parent="row3">
  <mxGeometry x="40" width="180" height="30" as="geometry">
    <mxRectangle width="180" height="30" as="alternateBounds"/>
  </mxGeometry>
</mxCell>
```

**관계선 (Crow's Foot):**

| 관계 | style |
|------|-------|
| 1:1 | `endArrow=ERzeroToOne;endFill=0;startArrow=ERzeroToOne;startFill=0;` |
| 1:N | `endArrow=ERmany;endFill=0;startArrow=ERmandOne;startFill=0;` |
| N:M | `endArrow=ERmany;endFill=0;startArrow=ERmany;startFill=0;` |
| 0..1:N | `endArrow=ERmany;endFill=0;startArrow=ERzeroToOne;startFill=0;` |

```xml
<!-- 1:N 관계선 예시 -->
<mxCell id="rel1" value="" style="edgeStyle=entityRelationEdgeStyle;fontSize=12;html=1;endArrow=ERmany;endFill=0;startArrow=ERmandOne;startFill=0;strokeWidth=1;strokeColor=#666666;" edge="1" parent="1" source="row3" target="entity2_row1"/>
```

**색상:**
- Entity 헤더: `fillColor=#f5f5f5;strokeColor=#666666` (연한 회색 배경)
- PK 텍스트: `fontColor=#cc0000` (빨강)
- FK 텍스트: `fontColor=#336699` (파랑)
- 관계선: `strokeColor=#666666`

**레이아웃:**
- `edgeStyle=entityRelationEdgeStyle` 사용 (직각 꺾임)
- Entity 간 간격: 200-300px
- 좌→우 또는 위→아래 방향으로 배치
- 관련 테이블끼리 가까이 배치

## 2. Flowchart (플로우차트)

**용도:** 업무 프로세스, 알고리즘, 의사결정 흐름을 표현할 때

**Shape 스타일:**

| 요소 | style |
|------|-------|
| 시작/끝 | `rounded=1;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;strokeWidth=2;fontSize=12;fontStyle=1;` |
| 처리 | `rounded=0;whiteSpace=wrap;fillColor=#f5f5f5;strokeColor=#999999;strokeWidth=1;fontSize=12;` |
| 판단 | `rhombus;whiteSpace=wrap;fillColor=#fff2cc;strokeColor=#d6b656;strokeWidth=2;fontSize=12;fontStyle=1;` |
| 입출력 | `shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;fillColor=#d5e8d4;strokeColor=#82b366;strokeWidth=1;fontSize=12;` |
| 서브프로세스 | `shape=process;whiteSpace=wrap;fillColor=#e1d5e7;strokeColor=#9673a6;strokeWidth=1;fontSize=12;` |

**화살표:**
```xml
<!-- 기본 흐름 -->
<mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;strokeWidth=1;strokeColor=#666666;fontSize=11;" edge="1" parent="1" source="n1" target="n2">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>

<!-- 판단 분기 (Yes/No 레이블) -->
<mxCell id="e2" value="Yes" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;strokeWidth=1;strokeColor=#666666;fontSize=11;fontStyle=1;labelBackgroundColor=#ffffff;" edge="1" parent="1" source="decision1" target="n3">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

**레이아웃:**
- 위→아래(세로) 흐름 기본, 복잡한 경우 좌→우도 가능
- 노드 간 세로 간격: 60-80px
- 판단 노드에서 분기 시 Yes는 아래, No는 오른쪽이 관례
- 화살표 레이블에 `labelBackgroundColor=#ffffff` 추가하여 겹침 방지

## 3. Sequence Diagram (시퀀스 다이어그램)

**용도:** API 호출 흐름, 시스템 간 메시지 교환 순서를 표현할 때

**요소 스타일:**
```xml
<!-- Actor/참여자 박스 -->
<mxCell id="actor1" value="Client" style="rounded=1;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;strokeWidth=2;fontSize=13;fontStyle=1;" vertex="1" parent="1">
  <mxGeometry x="60" y="20" width="100" height="40" as="geometry"/>
</mxCell>

<!-- Lifeline (점선 세로선) -->
<mxCell id="life1" value="" style="endArrow=none;dashed=1;strokeColor=#cccccc;strokeWidth=1;" edge="1" parent="1">
  <mxGeometry relative="1" as="geometry">
    <mxPoint x="110" y="60" as="sourcePoint"/>
    <mxPoint x="110" y="400" as="targetPoint"/>
  </mxGeometry>
</mxCell>

<!-- Activation 박스 (실행 구간) -->
<mxCell id="act1" value="" style="fillColor=#d9d9d9;strokeColor=#999999;strokeWidth=1;" vertex="1" parent="1">
  <mxGeometry x="103" y="80" width="14" height="60" as="geometry"/>
</mxCell>

<!-- 호출 메시지 (실선 화살표) -->
<mxCell id="msg1" value="1. 요청 전송" style="endArrow=open;endSize=12;dashed=0;strokeWidth=1;strokeColor=#666666;fontSize=11;fontStyle=1;labelBackgroundColor=#ffffff;html=1;" edge="1" parent="1">
  <mxGeometry relative="1" as="geometry">
    <mxPoint x="117" y="90" as="sourcePoint"/>
    <mxPoint x="303" y="90" as="targetPoint"/>
  </mxGeometry>
</mxCell>

<!-- 응답 메시지 (점선 화살표) -->
<mxCell id="msg2" value="2. 응답 반환" style="endArrow=open;endSize=12;dashed=1;strokeWidth=1;strokeColor=#666666;fontSize=11;labelBackgroundColor=#ffffff;html=1;" edge="1" parent="1">
  <mxGeometry relative="1" as="geometry">
    <mxPoint x="303" y="130" as="sourcePoint"/>
    <mxPoint x="117" y="130" as="targetPoint"/>
  </mxGeometry>
</mxCell>

<!-- 비동기 메시지 (열린 화살표 + 점선) -->
<mxCell id="msg3" value="3. 이벤트 발행" style="endArrow=open;endSize=12;dashed=1;dashPattern=5 3;strokeWidth=1;strokeColor=#999999;fontSize=11;labelBackgroundColor=#ffffff;html=1;" edge="1" parent="1">
  <mxGeometry relative="1" as="geometry">
    <mxPoint x="117" y="160" as="sourcePoint"/>
    <mxPoint x="503" y="160" as="targetPoint"/>
  </mxGeometry>
</mxCell>
```

**레이아웃:**
- 참여자 간 가로 간격: 180-220px
- 메시지 간 세로 간격: 40-50px
- 메시지에 번호 매기기 (`1. 요청 전송`, `2. 응답 반환`)로 순서 명확히
- 호출: 실선 / 응답: 점선으로 구분

## 4. System Architecture (시스템 아키텍처)

**용도:** 시스템 구성 요소와 레이어 구조를 표현할 때

**요소 스타일:**
```xml
<!-- 레이어 그룹 (swimlane) -->
<mxCell id="layer1" value="Presentation Layer" style="swimlane;startSize=28;fillColor=#f5f5f5;strokeColor=#999999;strokeWidth=1;fontSize=13;fontStyle=1;horizontal=1;swimlaneBody=1;collapsible=0;rounded=1;" vertex="1" parent="1">
  <mxGeometry x="20" y="20" width="760" height="120" as="geometry"/>
</mxCell>

<!-- 서비스 박스 -->
<mxCell id="svc1" value="User API" style="rounded=1;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;strokeWidth=1;fontSize=12;fontStyle=1;" vertex="1" parent="layer1">
  <mxGeometry x="20" y="40" width="120" height="50" as="geometry"/>
</mxCell>

<!-- DB (실린더) -->
<mxCell id="db1" value="PostgreSQL" style="shape=cylinder3;whiteSpace=wrap;boundedLbl=1;backgroundOutline=1;size=10;fillColor=#dae8fc;strokeColor=#6c8ebf;strokeWidth=1;fontSize=12;fontStyle=1;" vertex="1" parent="1">
  <mxGeometry x="100" y="300" width="100" height="70" as="geometry"/>
</mxCell>

<!-- 외부 서비스 (점선 박스) -->
<mxCell id="ext1" value="외부 API" style="rounded=1;whiteSpace=wrap;fillColor=#fff2cc;strokeColor=#d6b656;strokeWidth=1;dashed=1;fontSize=12;" vertex="1" parent="1">
  <mxGeometry x="400" y="300" width="120" height="50" as="geometry"/>
</mxCell>

<!-- 시스템 경계 (점선 그룹) -->
<mxCell id="boundary1" value="VPC" style="rounded=1;whiteSpace=wrap;fillColor=none;strokeColor=#999999;strokeWidth=2;dashed=1;dashPattern=8 4;fontSize=12;fontStyle=1;verticalAlign=top;align=left;spacingLeft=10;" vertex="1" parent="1">
  <mxGeometry x="10" y="10" width="500" height="380" as="geometry"/>
</mxCell>
```

**색상 역할:**
- 내부 서비스: `fillColor=#dae8fc;strokeColor=#6c8ebf` (파스텔 파랑)
- 외부 서비스: `fillColor=#fff2cc;strokeColor=#d6b656` (파스텔 노랑)
- DB/저장소: `fillColor=#e1d5e7;strokeColor=#9673a6` (파스텔 보라)
- 시스템 경계: `fillColor=none;strokeColor=#999999;dashed=1`
- 레이어 배경: `fillColor=#f5f5f5` (연한 회색)

**레이아웃:**
- 위→아래 레이어 구조 (Presentation → Business Logic → Data)
- 레이어 간 간격: 20-30px
- 레이어 내 서비스 간 간격: 40-60px
- 외부 시스템은 오른쪽 또는 아래에 별도 배치

## 5. BPMN Process (비즈니스 프로세스)

**용도:** 업무 절차, 승인 프로세스, 워크플로우를 표현할 때

**요소 스타일:**

| 요소 | style |
|------|-------|
| 시작 이벤트 | `ellipse;whiteSpace=wrap;aspect=fixed;fillColor=#d9d9d9;strokeColor=#666666;strokeWidth=2;fontSize=11;` |
| 종료 이벤트 | `ellipse;whiteSpace=wrap;aspect=fixed;fillColor=#d9d9d9;strokeColor=#333333;strokeWidth=4;fontSize=11;` |
| 태스크 | `rounded=1;whiteSpace=wrap;fillColor=#f5f5f5;strokeColor=#999999;strokeWidth=1;fontSize=12;` |
| 배타 게이트웨이 (XOR) | `rhombus;whiteSpace=wrap;fillColor=#fff2cc;strokeColor=#d6b656;strokeWidth=2;fontSize=11;fontStyle=1;` |
| 병렬 게이트웨이 (AND) | `rhombus;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;strokeWidth=2;fontSize=11;fontStyle=1;` |

```xml
<!-- Pool (가로 레인) -->
<mxCell id="pool1" value="담당부서" style="swimlane;startSize=24;fillColor=#f5f5f5;strokeColor=#999999;strokeWidth=1;fontSize=12;fontStyle=1;horizontal=1;childLayout=stackLayout;" vertex="1" parent="1">
  <mxGeometry x="20" y="20" width="700" height="120" as="geometry"/>
</mxCell>

<!-- 시작 이벤트 -->
<mxCell id="start" value="" style="ellipse;whiteSpace=wrap;aspect=fixed;fillColor=#d9d9d9;strokeColor=#666666;strokeWidth=2;" vertex="1" parent="pool1">
  <mxGeometry x="20" y="45" width="30" height="30" as="geometry"/>
</mxCell>

<!-- 태스크 -->
<mxCell id="task1" value="서류 접수" style="rounded=1;whiteSpace=wrap;fillColor=#f5f5f5;strokeColor=#999999;strokeWidth=1;fontSize=12;" vertex="1" parent="pool1">
  <mxGeometry x="80" y="30" width="120" height="60" as="geometry"/>
</mxCell>

<!-- 배타 게이트웨이 -->
<mxCell id="gw1" value="승인?" style="rhombus;whiteSpace=wrap;fillColor=#fff2cc;strokeColor=#d6b656;strokeWidth=2;fontSize=11;fontStyle=1;" vertex="1" parent="pool1">
  <mxGeometry x="240" y="30" width="60" height="60" as="geometry"/>
</mxCell>

<!-- 종료 이벤트 -->
<mxCell id="end" value="" style="ellipse;whiteSpace=wrap;aspect=fixed;fillColor=#d9d9d9;strokeColor=#333333;strokeWidth=4;" vertex="1" parent="pool1">
  <mxGeometry x="620" y="45" width="30" height="30" as="geometry"/>
</mxCell>
```

**레이아웃:**
- 좌→우 흐름 기본
- Pool/Lane으로 부서/역할 구분
- 게이트웨이에서 분기 시 레이블 필수 (Yes/No, 승인/반려)
- 이벤트(원): 30x30px, 태스크: 120x60px, 게이트웨이: 60x60px

## 6. State Diagram (상태 다이어그램)

**용도:** 객체의 상태 변화와 전이 조건을 표현할 때

**요소 스타일:**
```xml
<!-- 초기 상태 (검은 원) -->
<mxCell id="initial" value="" style="ellipse;whiteSpace=wrap;aspect=fixed;fillColor=#333333;strokeColor=#333333;strokeWidth=2;" vertex="1" parent="1">
  <mxGeometry x="20" y="55" width="20" height="20" as="geometry"/>
</mxCell>

<!-- 상태 (라운드 박스) -->
<mxCell id="state1" value="대기" style="rounded=1;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;strokeWidth=2;fontSize=12;fontStyle=1;" vertex="1" parent="1">
  <mxGeometry x="80" y="35" width="120" height="60" as="geometry"/>
</mxCell>

<!-- 종료 상태 (이중 원) -->
<mxCell id="final" value="" style="ellipse;whiteSpace=wrap;aspect=fixed;fillColor=#333333;strokeColor=#333333;strokeWidth=2;" vertex="1" parent="1">
  <mxGeometry x="540" y="52" width="26" height="26" as="geometry"/>
</mxCell>
<mxCell id="final_inner" value="" style="ellipse;whiteSpace=wrap;aspect=fixed;fillColor=#333333;strokeColor=#ffffff;strokeWidth=2;" vertex="1" parent="1">
  <mxGeometry x="545" y="57" width="16" height="16" as="geometry"/>
</mxCell>

<!-- 전이 (화살표 + 조건 레이블) -->
<mxCell id="trans1" value="요청 수신" style="edgeStyle=orthogonalEdgeStyle;rounded=1;strokeWidth=1;strokeColor=#666666;fontSize=11;fontStyle=0;labelBackgroundColor=#ffffff;endArrow=open;endSize=10;" edge="1" parent="1" source="state1" target="state2">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>

<!-- 자기 전이 (루프) -->
<mxCell id="self1" value="재시도" style="edgeStyle=orthogonalEdgeStyle;rounded=1;strokeWidth=1;strokeColor=#666666;fontSize=11;labelBackgroundColor=#ffffff;endArrow=open;endSize=10;" edge="1" parent="1" source="state2" target="state2">
  <mxGeometry x="-0.2" y="20" relative="1" as="geometry">
    <Array as="points">
      <mxPoint x="350" y="10"/>
      <mxPoint x="280" y="10"/>
    </Array>
    <mxPoint as="offset"/>
  </mxGeometry>
</mxCell>
```

**레이아웃:**
- 좌→우 흐름 (초기 상태 왼쪽, 종료 상태 오른쪽)
- 상태 간 간격: 120-160px
- 전이 레이블: `이벤트 / 액션` 형식 (예: `타임아웃 / 알림 발송`)
- 자기 전이는 상단 루프로 표현

## 7. Network/Infrastructure (네트워크/인프라)

**용도:** 서버 구성, 네트워크 토폴로지, 인프라 아키텍처를 표현할 때

**요소 스타일:**
```xml
<!-- 서버 -->
<mxCell id="server1" value="Web Server" style="shape=image;verticalLabelPosition=bottom;labelBackgroundColor=default;verticalAlign=top;aspect=fixed;imageAspect=0;image=img/lib/active_directory/generic_server.svg;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=11;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="48" height="60" as="geometry"/>
</mxCell>

<!-- DB 서버 -->
<mxCell id="db1" value="MySQL" style="shape=cylinder3;whiteSpace=wrap;boundedLbl=1;backgroundOutline=1;size=10;fillColor=#dae8fc;strokeColor=#6c8ebf;strokeWidth=1;fontSize=11;fontStyle=1;" vertex="1" parent="1">
  <mxGeometry x="300" y="100" width="80" height="60" as="geometry"/>
</mxCell>

<!-- 방화벽 -->
<mxCell id="fw1" value="Firewall" style="shape=mxgraph.network.firewall;fillColor=#f8cecc;strokeColor=#b85450;fontSize=11;fontStyle=1;verticalLabelPosition=bottom;verticalAlign=top;" vertex="1" parent="1">
  <mxGeometry x="50" y="200" width="60" height="50" as="geometry"/>
</mxCell>

<!-- 로드밸런서 -->
<mxCell id="lb1" value="ALB" style="rounded=1;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;strokeWidth=1;fontSize=11;fontStyle=1;" vertex="1" parent="1">
  <mxGeometry x="150" y="200" width="80" height="40" as="geometry"/>
</mxCell>

<!-- 클라우드/인터넷 -->
<mxCell id="cloud1" value="Internet" style="ellipse;shape=cloud;whiteSpace=wrap;fillColor=#f5f5f5;strokeColor=#999999;strokeWidth=1;fontSize=12;fontStyle=1;" vertex="1" parent="1">
  <mxGeometry x="20" y="20" width="120" height="60" as="geometry"/>
</mxCell>

<!-- 구역 (DMZ, Private 등) -->
<mxCell id="zone1" value="DMZ" style="rounded=1;whiteSpace=wrap;fillColor=none;strokeColor=#b85450;strokeWidth=2;dashed=1;dashPattern=8 4;fontSize=12;fontStyle=1;verticalAlign=top;align=left;spacingLeft=10;spacingTop=2;" vertex="1" parent="1">
  <mxGeometry x="30" y="170" width="300" height="120" as="geometry"/>
</mxCell>

<mxCell id="zone2" value="Private Subnet" style="rounded=1;whiteSpace=wrap;fillColor=none;strokeColor=#6c8ebf;strokeWidth=2;dashed=1;dashPattern=8 4;fontSize=12;fontStyle=1;verticalAlign=top;align=left;spacingLeft=10;spacingTop=2;" vertex="1" parent="1">
  <mxGeometry x="30" y="310" width="300" height="120" as="geometry"/>
</mxCell>
```

**구역별 색상:**
- DMZ 경계: `strokeColor=#b85450` (파스텔 빨강 점선)
- Private 경계: `strokeColor=#6c8ebf` (파스텔 파랑 점선)
- 서버/서비스: `fillColor=#dae8fc;strokeColor=#6c8ebf` (파스텔 파랑)
- 방화벽: `fillColor=#f8cecc;strokeColor=#b85450` (파스텔 빨강)
- 외부(인터넷/클라우드): `fillColor=#f5f5f5;strokeColor=#999999` (연한 회색)

**레이아웃:**
- 위→아래 (인터넷 → DMZ → Private → DB)
- 구역별 점선 박스로 네트워크 경계 명시
- 서버 아이콘은 `verticalLabelPosition=bottom`으로 아래에 이름 배치
- 연결선: `edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#999999`

## 8. mxGraph 스텐실 & 커스텀 아이콘 가이드

### 내장 스텐실 목록

draw.io에서 사용 가능한 주요 스텐실 라이브러리:

| 라이브러리 | prefix | 주요 Shape |
|------------|--------|------------|
| Network | `mxgraph.network.` | `server`, `firewall`, `router`, `load_balancer`, `cloud` |
| AWS 3 | `mxgraph.aws3.` | `ec2`, `rds`, `s3`, `lambda`, `vpc`, `elb` |
| AWS 4 | `mxgraph.aws4.` | `resourceIcon`, `productIcon` (신형 아이콘) |
| Flowchart | `mxgraph.flowchart.` | `decision`, `document`, `stored_data`, `delay` |
| Basic | `mxgraph.basic.` | `rect`, `rounded_rect`, `cloud`, `star` |
| 내장 | `shape=` | `cylinder3`, `ellipse`, `rhombus`, `parallelogram`, `process`, `hexagon` |

**사용 예시:**
```xml
<!-- AWS Lambda -->
<mxCell style="shape=mxgraph.aws3.lambda;fillColor=#F58536;gradientColor=none;fontSize=11;" .../>

<!-- 네트워크 서버 -->
<mxCell style="shape=mxgraph.network.server;fillColor=#dae8fc;fontSize=11;" .../>
```

### 커스텀 SVG 아이콘 삽입

draw.io에서 외부 이미지나 SVG를 노드로 사용할 수 있습니다:

```xml
<!-- URL 이미지 아이콘 -->
<mxCell id="icon1" value="모니터링" style="shape=image;verticalLabelPosition=bottom;labelBackgroundColor=default;verticalAlign=top;aspect=fixed;imageAspect=0;image=https://cdn-icons-png.flaticon.com/128/2991/2991106.png;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="48" height="48" as="geometry"/>
</mxCell>

<!-- Base64 인코딩 SVG 아이콘 -->
<mxCell id="icon2" value="커스텀" style="shape=image;verticalLabelPosition=bottom;labelBackgroundColor=default;verticalAlign=top;aspect=fixed;imageAspect=0;image=data:image/svg+xml,PHN2ZyB4bWxucz0i...;" vertex="1" parent="1">
  <mxGeometry x="200" y="100" width="48" height="48" as="geometry"/>
</mxCell>
```

### HTML Label + 아이콘 조합

노드 안에 HTML과 아이콘을 함께 사용하는 패턴:

```xml
<!-- 아이콘 + 텍스트 조합 노드 -->
<mxCell id="combo1" value="&lt;b&gt;API Gateway&lt;/b&gt;&lt;br&gt;&lt;font style='font-size:10px;color:#999999'&gt;Kong / Nginx&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;strokeWidth=1;fontSize=12;verticalAlign=middle;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="140" height="60" as="geometry"/>
</mxCell>

<!-- 이미지 + 텍스트 수직 배치 -->
<mxCell id="combo2" value="Redis" style="shape=image;verticalLabelPosition=bottom;labelBackgroundColor=default;verticalAlign=top;aspect=fixed;imageAspect=0;image=img/lib/active_directory/generic_server.svg;fontSize=11;fontStyle=1;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="40" height="50" as="geometry"/>
</mxCell>
```

### draw.io 내장 이미지 경로

draw.io에서 기본 제공하는 이미지 경로 (`image=img/lib/...`):

| 카테고리 | 경로 | 주요 아이콘 |
|----------|------|------------|
| Active Directory | `img/lib/active_directory/` | `generic_server.svg`, `database.svg` |
| Clipart | `img/lib/clip_art/` | `computers/`, `networking/` |

## 9. 공통 레이아웃 & 엣지 패턴

### edgeStyle 종류

| edgeStyle | 용도 | 설명 |
|-----------|------|------|
| `orthogonalEdgeStyle` | **기본 권장** | 직각 꺾임, 대부분의 다이어그램에 적합 |
| `entityRelationEdgeStyle` | ERD | Entity 간 관계선에 최적화 |
| `elbowEdgeStyle` | 간단한 꺾임 | 단순 L자 꺾임 |
| (미지정) | 직선 | 직선 연결, 시퀀스 다이어그램 메시지에 적합 |

### 화살표 종류 (startArrow / endArrow)

| 값 | 모양 | 용도 |
|----|------|------|
| `open` | 열린 삼각형 | 일반 흐름, 메시지 |
| `classic` | 채운 삼각형 | 강한 방향성 |
| `block` | 채운 사각 삼각형 | 의존성 |
| `diamond` | 다이아몬드 | UML 집합(aggregation) |
| `diamondThin` | 빈 다이아몬드 | UML 합성(composition) |
| `ERone` | 단일선 | ERD 1 |
| `ERmandOne` | 단일선+가로선 | ERD 필수 1 |
| `ERmany` | 까마귀발 | ERD 다(N) |
| `ERzeroToOne` | 원+선 | ERD 0..1 |
| `ERzeroToMany` | 원+까마귀발 | ERD 0..N |
| `ERoneToMany` | 선+까마귀발 | ERD 1..N |
| `none` | 없음 | 양방향/무방향 |

### 그리드 정렬 규칙

- 기본 그리드: 20px 단위 (`gridSize="10"`, 스냅 시 20px)
- 노드 위치는 20의 배수로 설정 (`x="40" y="60"`)
- 노드 크기도 20의 배수 권장 (`width="120" height="60"`)
- 노드 간 최소 간격: 40px

### mxGraphModel 기본 템플릿

모든 다이어그램의 기본 XML 구조:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxfile>
  <diagram name="다이어그램 제목" id="diagram-001">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1"
                  tooltips="1" connect="1" arrows="1" fold="1" page="1"
                  pageScale="1" pageWidth="1200" pageHeight="800"
                  math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <!-- 여기에 노드와 엣지 추가 -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

**pageWidth/pageHeight:** 다이어그램 크기에 맞게 조정. 일반적으로 너비 1000-1400, 높이 600-1000.
**dx/dy:** 캔버스 오프셋. pageWidth/pageHeight와 동일하게 설정 권장.
