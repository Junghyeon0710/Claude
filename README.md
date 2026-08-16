# Claude — Unreal Engine MCP 자동화 저장소

Unreal Engine **5.8** 프로젝트. 에디터를 손으로 조작하는 대신 **MCP(Model Context Protocol) 툴 호출로 제작**한 결과물을 모아둔 저장소입니다. 메시가 필요하면 **Blender MCP**로 만들어 FBX로 넘기고, 레벨 배치·머티리얼·그래프 구성·검증 캡처까지 전부 코드로 수행합니다.

사용 플러그인: `ModelContextProtocol`, `EditorToolset`, `PCGToolset`, `UMGToolSet`, `AllToolsets`

<table>
<tr>
<td width="33%"><a href="#1-pcg-절차적-숲"><img src="docs/images/01_overview.jpg" width="100%"></a></td>
<td width="33%"><a href="#2-나이아가라-vfx"><img src="docs/images/09_vfx_fire.jpg" width="100%"></a></td>
<td width="33%"><a href="#3-시퀀서-시네마틱"><img src="docs/images/14_seq_pullback.jpg" width="100%"></a></td>
</tr>
<tr>
<td align="center"><b>PCG 절차적 숲</b><br>인스턴스 70,325</td>
<td align="center"><b>나이아가라 VFX</b><br>시스템 5종 · 에미터 23</td>
<td align="center"><b>시퀀서 시네마틱</b><br>42초 · 6샷</td>
</tr>
</table>

## 목차

| # | 작업 | 규모 | 폴더 |
|---|---|---|---|
| [1](#1-pcg-절차적-숲) | **PCG 절차적 숲** | 그래프 93노드 / 인스턴스 70,325 / 지형 600m | `Content/PCG_Test` |
| [2](#2-나이아가라-vfx) | **나이아가라 VFX** | 시스템 5종 / 에미터 23 / 머티리얼 3종 | `Content/VFX_Test` |
| [3](#3-시퀀서-시네마틱) | **시퀀서 시네마틱** | 1260프레임 / 6샷 / 카메라 6대 | `Content/VFX_Test` |
| [4](#4-그-외-작업) | 그 외 작업 | 모듈러 킷 · UMG 재현 | 여러 폴더 |

각 항목은 **결과 → 파이프라인 → 재현 방법 → 기술 노트** 순서로 정리했습니다.
기술 노트에는 MCP로 막힌 지점과 우회책을 적어뒀습니다(접혀 있습니다).

---

# 1. PCG 절차적 숲

> `Content/PCG_Test`

규칙만 주면 나무·바위·관목·풀이 알아서 자라는 PCG 그래프. 나무를 한 그루도 손으로 심지 않았고, **지형을 400m에서 600m로 교체했을 때 70,325개가 자동으로 재배치**됐습니다.

![전체 조망](docs/images/01_overview.jpg)

![지상 시점](docs/images/02_road_ground.jpg)

## 1.1 결과

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

## 1.2 파이프라인

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

## 1.3 생태 규칙

**설선** — 고도 상한을 넘으면 나무가 사라지고 바위만 남습니다.

![설선](docs/images/03_snowline.jpg)

**경사 편중 + 근접 밀집** — 왼쪽 완경사는 숲, 오른쪽 급사면은 나무 없이 바위. 관목은 나무 주변에만 붙습니다.

![생태 규칙](docs/images/04_ecology.jpg)

**길** — 스플라인을 지형에 투영해 세그먼트 메시를 이어 붙이고, `Difference`로 폭 900 내 나무·바위를 제거합니다. 가장자리엔 풀·관목·자갈이 남습니다.

![길](docs/images/05_road_high.jpg)

**개체 변화** — 같은 메시에 색조가 다른 MaterialInstance를 물려 침엽수 3톤 / 활엽수 3톤으로 갈립니다. Z축만 0.75–1.38배 흔들어 키도 다릅니다.

![색 변화](docs/images/06_color_variants.jpg)

## 1.4 에셋 (Blender MCP 제작)

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

## 1.5 재현

1. `Content/PCG_Test/L_PCG_Forest` 열기
2. 아웃라이너에서 `PCG_ForestVolume` 선택
3. Details → PCG Component → **Generate**

파라미터를 바꾸려면 `PCG_ForestGraph`에서 각 브랜치의 `Surface Sampler`(밀도), `Density Filter`(임계값), `Filter by Range`(고도)를 조정합니다. 개수 확인은 노드 우클릭 → **Inspect**.

## 1.6 기술 노트

<details>
<summary><b>MCP로 막힌 것들 — 5건 (펼치기)</b></summary>

**랜드스케이프를 PCG로 샘플링할 수 없습니다.** `Get Landscape Data`가 항상 빈 결과를 냅니다. 원인은 `PCGWorldActor.LandscapeCache`의 `cacheEntryCount`가 0인 것인데, 이 캐시를 빌드하는 경로가 MCP에 없습니다(콘솔 *명령* 실행 툴도 없어 우회 불가). `serializationMode` 변경, 랜드스케이프 더티 마킹, `Wait Until Landscape Is Ready` 삽입 모두 실패했습니다.
→ **우회**: 지형 메시를 `CTF_UseComplexAsSimple` 콜리전으로 두고 `World Ray Hit Query`로 표면을 얻습니다. 노멀도 정상이라 경사 규칙이 전부 동작합니다.

**`Spawn Spline Mesh`는 사용 불가.** 그래프에 넣으면 `ExecuteGraphInstance`가 실패하고, 노드를 지워도 볼륨이 망가진 채 남습니다(볼륨 재스폰으로만 복구). 길은 Static Mesh Spawner로 세그먼트를 이어 붙여 만들었습니다.

**인스턴스별 랜덤 색은 머티리얼 표현식으로 안 됩니다.** `PerInstanceRandom`, `PerInstanceCustomData` 모두 PCG가 만든 ISM에서 값을 못 받습니다(PCG 쪽 어트리뷰트 생성은 정상 확인). descriptor에 `numCustomDataFloats`가 노출되지 않는 것이 원인으로 보입니다.
→ **우회**: `MeshEntries` descriptor의 `OverrideMaterials`로 같은 메시에 색만 다른 MIC를 물립니다.

**그래프 파라미터 → 노드 바인딩은 됩니다.** `Get Graph Parameter` 노드를 만들고 `ConnectNodePins`의 대상 핀 라벨에 **노드 프로퍼티 이름을 그대로** 주면 오버라이드 핀에 연결됩니다(`GetSlopeCos.Out → SlopeCut.LowerBound`). 단 중첩 구조체 프로퍼티(고도 필터의 threshold 등)는 오버라이드 핀이 없어 파라미터화가 안 됩니다.

**튜닝은 실측 분포로.** Density Filter 임계값을 감으로 잡으면 안 됩니다. 노이즈 출력이 0.51–1.0 범위인데 임계값 0.55를 주면 아무것도 안 걸러집니다. `GetNodeDataView`(에디터의 Inspect)로 실제 분포를 읽어 목표 개수의 백분위에서 역산해야 합니다. 그리고 **Self Pruning이 개수의 천장**이라, 샘플을 늘려도 안 늘면 `pointExtents`(= 최소간격 ÷ 2)를 줄이는 것이 유일한 손잡이입니다.

</details>

---

# 2. 나이아가라 VFX

> `Content/VFX_Test`

나이아가라 시스템 5종을 에디터 UI 없이 만들었습니다. **에미터 23개, 스택 에러 0, 전 시스템 컴파일 UpToDate.** 색·크기 그라데이션은 커브를 쓰지 않고 **HLSL 표현식으로 생성**했습니다 — 커브 DataInterface에 값을 쓰면 에디터가 죽기 때문입니다.

<table>
<tr>
<td width="50%"><img src="docs/images/09_vfx_fire.jpg" width="100%"></td>
<td width="50%"><img src="docs/images/10_vfx_aurora.jpg" width="100%"></td>
</tr>
<tr>
<td><b>NS_Fire</b> — 흰노랑→주황→적색 HDR 램프, 불티, 라이트 렌더러</td>
<td><b>NS_Aurora</b> — 세로 시트 커튼 3겹, 녹색→청록→보라</td>
</tr>
<tr>
<td><img src="docs/images/11_vfx_tornado.jpg" width="100%"></td>
<td><img src="docs/images/12_vfx_water.jpg" width="100%"></td>
</tr>
<tr>
<td><b>NS_Tornado</b> — 반경이 커지는 원통 밴드 5겹 + VortexForce</td>
<td><b>NS_WaterFountain</b> — Velocity-aligned 물줄기, 중력 포물선</td>
</tr>
<tr>
<td><img src="docs/images/13_vfx_lightning.jpg" width="100%"></td>
<td></td>
</tr>
<tr>
<td><b>NS_Lightning</b> — HDR 볼트 + JitterPosition 지그재그, 2.4초 주기 플래시</td>
<td></td>
</tr>
</table>

## 2.1 결과

| 시스템 | 에미터 | 구성 | 핵심 기법 |
|---|---:|---|---|
| NS_Fire | 4 | Core / Embers / Smoke / **Light** | Curl Noise, HDR 램프, 라이트 렌더러 |
| NS_Aurora | 3 | Lower / Mid / Upper | 세로 non-uniform 스프라이트, 초저속 드리프트 |
| NS_Tornado | 7 | Band0–4 / GroundDust / **Debris(Mesh)** | VortexForce, 높이별 반경 확장 |
| NS_WaterFountain | 4 | Jet / Droplets / Mist / Splash | VelocityAligned 스트레치, 중력 −980 |
| NS_Lightning | 5 | MainBolt / Glow / Branch×2 / Sparks | JitterPosition, 시간 게이트 플래시 |
| **합계** | **23** | | |

머티리얼 3종(`M_VFX_Translucent` / `TranslucentRibbon` / `Additive`)은 엔진 기본 나이아가라 머티리얼을 복제해 블렌드 모드만 바꿔 만들었습니다.

## 2.2 파이프라인

모든 스프라이트 에미터가 `Fountain` 템플릿에서 출발해 같은 뼈대를 공유합니다.

```
CreateNiagaraSystem (MinimalLightweight)   시스템 생성 → 템플릿 에미터 제거
      │
      ├─ AddEmitter (Fountain / UpwardMeshBurst)
      │
      ├─ EmitterUpdate   SpawnRate
      ├─ ParticleSpawn   InitializeParticle  수명·크기·색 모드
      │                  ShapeLocation       Cylinder / Cone 분포
      │                  AddVelocity         원뿔 방향 + 속도 범위
      ├─ ParticleUpdate  GravityForce / Drag
      │                  CurlNoiseForce      난류
      │                  VortexForce         회전 (토네이도)
      │                  JitterPosition      각진 변위 (번개)
      │                  ScaleColor          ← HLSL 램프 (RGB·Alpha)
      │                  ScaleSpriteSize     ← HLSL 램프
      │                  SolveForcesAndVelocity
      └─ SetRendererData  머티리얼 / 정렬 / 정렬힌트
                          └ ApplyStackIssueFix 로 솔버 순서 자동 교정
```

`ScaleColor`의 `Scale RGB`·`Scale Alpha`에 중첩 `lerp` 문자열을 넣어 다단 그라데이션을 만듭니다. 불꽃 코어는 이렇게 펼쳐집니다.

```hlsl
lerp(lerp(lerp(float3(12,7,2), float3(8,3.2,0.5),
     saturate((Particles.NormalizedAge - 0.0) * 6.667)),
     float3(3.5,0.9,0.08), saturate((Particles.NormalizedAge - 0.15) * 4.0)), ...)
```

`Particles.NormalizedAge`, `Particles.Position`, `Engine.Time`을 참조할 수 있어 커브보다 표현력이 넓습니다.

## 2.3 재현

1. `Content/VFX_Test/L_VFX_Showcase` 열기
2. 레벨의 `FX_Showcase_*` 액터에서 개별 확인
3. 파티클이 안 보이면 **Simulate**를 켜세요 (에디터 뷰포트는 나이아가라를 tick하지 않습니다)

## 2.4 기술 노트

<details>
<summary><b>MCP로 막힌 것들 — 4건 (펼치기)</b></summary>

**커브 DataInterface에 쓰면 에디터가 크래시합니다.** `ScaleColor.Linear Color Curve` 같은 커브 입력에 `SetStackInputData`를 하면 `PlaceholderDataInterfaceChanged → ResetSystem`이 컴파일 중에 재진입해 `InitDITickLists`에서 널 참조로 죽습니다.
→ **우회**: HLSL 표현식 입력(`NiagaraExt_StackInputData_HlslExpression`)으로 전량 대체. 크래시가 없을 뿐 아니라 표현력도 더 좋습니다.

**`ShapeLocation`의 Box/Plane 셰이프는 파티클이 나오지 않습니다.** Cylinder·Cone은 정상입니다. 오로라가 렌더되지 않던 원인이었고, 원통 분포로 바꾸자 즉시 해결됐습니다. 원뿔은 파티클이 넓은 끝에 몰리므로, 테이퍼 실루엣은 **반경이 커지는 원통 밴드를 쌓는 편**이 예측 가능합니다(토네이도가 그 방식).

**빔(DynamicBeam) 리본은 신뢰할 수 없습니다.** `Use Beam Tangents`의 기본 탄젠트가 0이라 빔이 통째로 붕괴하고, 고쳐도 상대좌표 Start/End가 지정한 길이보다 훨씬 짧게 그려집니다. 오로라·번개 모두 스프라이트 방식으로 선회했습니다.

**그 외 자잘한 것** — `SetEmitterData`는 `bEnabled`가 아니라 **`bIsEnabled`**, 렌더러 프로퍼티는 PascalCase(camelCase는 에러 없이 무시), 스태틱 스위치로 숨겨진 입력은 부모 스위치를 바꿔도 **다음 호출에서 즉시 반영되지 않습니다**.

</details>

---

# 3. 시퀀서 시네마틱

> `Content/VFX_Test`

VFX 5종을 훑는 **42초(1260프레임 @ 30fps) 6샷** 시퀀스 `LS_VFX_Showcase`. 샷마다 스포너블 시네카메라를 하나씩 두고 트랜스폼과 **초점거리를 함께 키프레임**했습니다.

![풀백](docs/images/14_seq_pullback.jpg)

## 3.1 샷 구성

| # | 대상 | 구간 | 카메라 워크 | 렌즈 |
|---|---|---|---|---|
| 1 | 오로라 | 0–8s | 좌→우 수평 트래킹 | 16.5mm |
| 2 | 토네이도 | 8–16s | 로우앵글 크레인 업 + 오빗 | 23.5 → 30mm |
| 3 | 번개 | 16–23s | 정지에 가까운 푸시인 | 25.7 → 32.5mm |
| 4 | 분수 | 23–31s | 시계방향 오빗 | 28.3 → 34.6mm |
| 5 | 불 | 31–38s | 클로즈업 회전 | 43.5 → 55.4mm |
| 6 | 풀백 | 38–42s | 상공으로 후퇴, 전체 조망 | 34.6 → 16.5mm |

<table>
<tr>
<td width="50%"><img src="docs/images/15_seq_aurora.jpg" width="100%"></td>
<td width="50%"><img src="docs/images/16_seq_tornado.jpg" width="100%"></td>
</tr>
<tr>
<td>샷 1 — 오로라 (상공 배치, 전 샷의 하늘 배경)</td>
<td>샷 2 — 토네이도 (로우앵글)</td>
</tr>
</table>

오로라는 상공 z=7000에 배치해 **모든 샷의 하늘 배경**으로 쓰고, 나머지는 서로 화면에 겹치지 않도록 X·Y축에 분산했습니다. 초점거리를 키프레임하지 않으면 시네카메라 기본 35mm가 고정되어 풀백 샷에 아무것도 들어오지 않습니다.

## 3.2 재현

1. `Content/VFX_Test/L_VFX_Showcase` 열기
2. 시퀀서에서 `LS_VFX_Showcase` 재생

## 3.3 기술 노트

<details>
<summary><b>MCP로 막힌 것들 — 4건 (펼치기)</b></summary>

**`set_camera_cut_binding`은 항상 실패합니다.** 어떤 ID 형식을 줘도 `call() takes at most 0 arguments`.
→ **우회**: `ObjectTools.set_properties(section, {"CameraBindingID": {"Guid": <bindingId>, "SequenceID": 0, "ResolveParentIndex": 0}})`로 섹션 프로퍼티를 직접 씁니다.

**시퀀서를 연 채 PIE를 시작하면 죽습니다.** `OnPreBeginPIE → OnPlaybackContextChanged → SpawnRegister::CleanUp → DestroySpawnedObject → AActor::Modify`. 레벨에 남은 스폰 카메라도 `ACineCameraActor::Tick`에서 무효 핸들로 죽습니다.
→ 결과적으로 **시퀀서 카메라 뷰는 스크린샷으로 검증할 수 없습니다.** 나이아가라는 시퀀서 재생만으로 충분히 tick하지 않아 화면이 비고, 파티클을 돌리려면 Simulate가 필요한데 그것이 시퀀서와 공존하지 않습니다. 샷 포즈를 좌표로 직접 캡처해 검증했습니다. 실제 영상은 Movie Render Queue가 답입니다.

**노출을 고정하지 않으면 튜닝이 무의미합니다.** 어두운 씬에서 자동 노출이 열려 additive VFX가 전부 흰색으로 포화됩니다. `AutoExposureMethod: AEM_Manual` + Min=Max=1인 언바운드 PostProcessVolume이 필요합니다.

**거리 컬링은 복구되지 않습니다.** Simulate 중 카메라에서 먼 나이아가라는 컬링되어 꺼지는데, 카메라가 돌아와도 되살아나지 않습니다. 여러 이펙트를 한 세션에서 순회 캡처하면 뒤쪽 것이 조용히 빈 화면으로 나옵니다 — 대상마다 Simulate를 다시 시작해야 합니다. 프레임 단위는 tick이 아닌 **display rate** 기준입니다.

</details>

---

# 4. 그 외 작업

| 폴더 | 내용 |
|---|---|
| `Content/IndustrialHarbor_Claude` | 산업 항구 모듈러 킷. Blender 제작 메시 90개, 텍스처 81장, 마스터 머티리얼 3종 + MI 56개, 레벨 액터 1,720개 |
| `Content/KoreanOldTown` | 한국 구도심 프롭·모듈러 세트 |
| `Content/UIReferenceTest` | UMG 레이아웃 재현 (WBP 8종 + 텍스처 15종) |
