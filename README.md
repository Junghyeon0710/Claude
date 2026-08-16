# Claude — Unreal Engine MCP 자동화 저장소

Unreal Engine **5.8** 프로젝트. 에디터를 손으로 조작하는 대신 **MCP(Model Context Protocol) 툴 호출로 제작**한 결과물을 모아둔 저장소입니다. 메시가 필요하면 **Blender MCP**로 만들어 FBX로 넘기고, 레벨 배치·머티리얼·그래프 구성·검증 캡처까지 전부 코드로 수행합니다.

사용 플러그인: `ModelContextProtocol`, `EditorToolset`, `PCGToolset`, `UMGToolSet`, `AllToolsets`

---

# PCG 절차적 숲 (`Content/PCG_Test`)

규칙만 주면 나무·바위·관목·풀이 알아서 자라는 PCG 그래프. 나무를 한 그루도 손으로 심지 않았고, **지형을 400m에서 600m로 교체했을 때 70,325개가 자동으로 재배치**됐습니다.

![전체 조망](docs/images/01_overview.jpg)

![지상 시점](docs/images/02_road_ground.jpg)

## 결과

| 레이어 | 메시 | 인스턴스 | 규칙 |
|---|---|---:|---|
| L1 대형 침엽수 | Pine A/B | 2,216 | 고도 1825–6290, 경사 ≤25°, 북사면 선호 |
| L2 중형 활엽수 | Broad A/B, Dead | 5,171 | 고도 100–6290, 경사 ≤30°, 남사면 선호 |
| L3 관목 | Bush A | 25,095 | 활엽수 근접 시에만 (Distance 가중) |
| L4 바위 | Rock A/B/C | 1,386 | 경사 반전 — 급경사일수록 밀집 |
| L5 풀 | Grass A | 31,617 | 고도 ≤5670, 경사 ≤20°, 겹침 허용 |
| L6 저지대 관목 | Bush A | 4,434 | 고도 ≤1690 전담, 밀도 2배 |
| 길 + 자갈 | Road_Segment, Rock A | 406 | 스플라인 추종, 폭 900 내 나무·바위 제거 |
| **합계** | | **70,325** | |

- 그래프 **93 노드 / 101 에지 / 7 브랜치**
- 지형 600m × 600m, 고도 100–9096 유닛
- 서브그래프 `PCG_ScatterLayer` (파라미터 6종) + 재사용 데모 `PCG_BiomeDemo`

## 파이프라인

모든 브랜치가 같은 6단계 뼈대를 공유하고 숫자만 다릅니다.

```
World Ray Hit Query          지형 표면 획득
      │
      ├─ ① Surface Sampler          격자 후보 포인트
      ├─ ② Normal To Density        경사 → 밀도
      │    Normal To Density        사면 방위(남/북) → 밀도 배수
      │    Spatial Noise (FBM)      펄린 노이즈 → 밀도 (숲 뭉침·빈터)
      │    Filter by Range          고도 컷 (설선 / 저지대)
      │    Distance                 나무까지 거리 → 밀도 (관목 전용)
      ├─ ③ Density Filter           임계값 미만 제거
      │    Self Pruning             최소 간격 이내 제거
      ├─ ④ Transform Points         랜덤 Yaw/스케일/지터 + Z 높이 변조
      ├─ ⑤ Projection               지형 표면에 스냅
      └─ ⑥ Static Mesh Spawner      ISM 인스턴스 생성
                                     └ Difference 로 길 위 제거
```

`$Density`가 기축통화입니다. ②에서 규칙을 밀도에 누적하고 ③에서 실행합니다.

## 생태 규칙

**설선** — 고도 상한을 넘으면 나무가 사라지고 바위만 남습니다.

![설선](docs/images/03_snowline.jpg)

**경사 편중 + 근접 밀집** — 왼쪽 완경사는 숲, 오른쪽 급사면은 나무 없이 바위. 관목은 나무 주변에만 붙습니다.

![생태 규칙](docs/images/04_ecology.jpg)

**길** — 스플라인을 지형에 투영해 세그먼트 메시를 이어 붙이고, `Difference`로 폭 900 내 나무·바위를 제거합니다. 가장자리엔 풀·관목·자갈이 남습니다.

![길](docs/images/05_road_high.jpg)

**개체 변화** — 같은 메시에 색조가 다른 MaterialInstance를 물려 침엽수 3톤 / 활엽수 3톤으로 갈립니다. Z축만 0.75–1.38배 흔들어 키도 다릅니다.

![색 변화](docs/images/06_color_variants.jpg)

## 에셋 (Blender MCP 제작)

전부 로우폴리로 스크립트 생성 → FBX → 임포트했습니다. 원본 FBX는 `ImportSource/`에 있습니다.

![Blender 에셋](docs/images/07_blender_assets.jpg)

| 에셋 | 트라이앵글 | 높이 |
|---|---:|---|
| Tree_Pine_A / B | 116 / 94 | 10.1m / 14m |
| Tree_Broad_A / B | 108 / 188 | 8.1m / 11.2m |
| Tree_Dead | 128 | 6.4m |
| Rock_A / B / C | 44 each | 1.1 / 2.0 / 4.2m |
| Bush_A / Grass_A | 80 / 6 | 1.3m / 0.5m |
| Terrain_Forest | 80,802 | 600m, 기복 90m |
| Road_Segment | 40 | 폭 9.2m |

원점은 전부 밑동 바닥 중앙, +Z 업, 트랜스폼 적용 완료 (미터 단위 모델링 → 언리얼에서 1m = 100유닛 정확히 일치).

**접지 검증** — Projection이 정상 동작해 밑동이 뜨거나 묻히지 않습니다.

![접지](docs/images/08_projection.jpg)

## 재현

1. `Content/PCG_Test/L_PCG_Forest` 열기
2. 아웃라이너에서 `PCG_ForestVolume` 선택
3. Details → PCG Component → **Generate**

파라미터를 바꾸려면 `PCG_ForestGraph`에서 각 브랜치의 `Surface Sampler`(밀도), `Density Filter`(임계값), `Filter by Range`(고도)를 조정합니다. 개수 확인은 노드 우클릭 → **Inspect**.

## 기술 노트 — MCP로 막힌 것들

이 프로젝트에서 확인된 한계입니다. 같은 작업을 하려는 사람에게 유용할 내용입니다.

**랜드스케이프를 PCG로 샘플링할 수 없습니다.** `Get Landscape Data`가 항상 빈 결과를 냅니다. 원인은 `PCGWorldActor.LandscapeCache`의 `cacheEntryCount`가 0인 것인데, 이 캐시를 빌드하는 경로가 MCP에 없습니다(콘솔 *명령* 실행 툴도 없어 우회 불가). `serializationMode` 변경, 랜드스케이프 더티 마킹, `Wait Until Landscape Is Ready` 삽입 모두 실패했습니다.
→ **우회**: 지형 메시를 `CTF_UseComplexAsSimple` 콜리전으로 두고 `World Ray Hit Query`로 표면을 얻습니다. 노멀도 정상이라 경사 규칙이 전부 동작합니다.

**`Spawn Spline Mesh`는 사용 불가.** 그래프에 넣으면 `ExecuteGraphInstance`가 실패하고, 노드를 지워도 볼륨이 망가진 채 남습니다(볼륨 재스폰으로만 복구). 길은 Static Mesh Spawner로 세그먼트를 이어 붙여 만들었습니다.

**인스턴스별 랜덤 색은 머티리얼 표현식으로 안 됩니다.** `PerInstanceRandom`, `PerInstanceCustomData` 모두 PCG가 만든 ISM에서 값을 못 받습니다(PCG 쪽 어트리뷰트 생성은 정상 확인). descriptor에 `numCustomDataFloats`가 노출되지 않는 것이 원인으로 보입니다.
→ **우회**: `MeshEntries` descriptor의 `OverrideMaterials`로 같은 메시에 색만 다른 MIC를 물립니다.

**그래프 파라미터 → 노드 바인딩은 됩니다.** `Get Graph Parameter` 노드를 만들고 `ConnectNodePins`의 대상 핀 라벨에 **노드 프로퍼티 이름을 그대로** 주면 오버라이드 핀에 연결됩니다(`GetSlopeCos.Out → SlopeCut.LowerBound`). 단 중첩 구조체 프로퍼티(고도 필터의 threshold 등)는 오버라이드 핀이 없어 파라미터화가 안 됩니다.

**튜닝은 실측 분포로.** Density Filter 임계값을 감으로 잡으면 안 됩니다. 노이즈 출력이 0.51–1.0 범위인데 임계값 0.55를 주면 아무것도 안 걸러집니다. `GetNodeDataView`(에디터의 Inspect)로 실제 분포를 읽어 목표 개수의 백분위에서 역산해야 합니다. 그리고 **Self Pruning이 개수의 천장**이라, 샘플을 늘려도 안 늘면 `pointExtents`(= 최소간격 ÷ 2)를 줄이는 것이 유일한 손잡이입니다.

---

# 그 외 작업

| 폴더 | 내용 |
|---|---|
| `Content/IndustrialHarbor_Claude` | 산업 항구 모듈러 킷. Blender 제작 메시 90개, 텍스처 81장, 마스터 머티리얼 3종 + MI 56개, 레벨 액터 1,720개 |
| `Content/KoreanOldTown` | 한국 구도심 프롭·모듈러 세트 |
| `Content/UIReferenceTest` | UMG 레이아웃 재현 (WBP 8종 + 텍스처 15종) |
| `Content/VFX_Test` | 나이아가라 VFX 5종 (불/오로라/토네이도/분수/번개) |
