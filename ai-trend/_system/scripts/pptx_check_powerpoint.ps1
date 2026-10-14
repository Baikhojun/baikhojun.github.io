param(
    [Parameter(Mandatory = $true)][string]$Pptx,
    [string]$OutDir = ""
)
# PowerPoint 실제 배치로 PPTX 넘침을 검사하고(선택) 슬라이드를 PNG 로 내보낸다. (Windows + PowerPoint 필요, 검수용)
#  - 글상자: 실제 글자 영역(BoundTop+BoundHeight)이 상자 아래·오른쪽을 넘는가
#  - 본문 도형·표: 바닥글 선(6.92in = 498pt)을 침범하는가, 슬라이드 밖으로 나가는가
# 사용: powershell -File pptx_check_powerpoint.ps1 -Pptx report.pptx [-OutDir 렌더폴더]
# PowerPoint 가 이미 실행 중이면 사용자의 문서를 건드리지 않도록 검사하지 않고 끝낸다.
$ErrorActionPreference = "Stop"
if (Get-Process POWERPNT -ErrorAction SilentlyContinue) {
    Write-Output '{"skipped": "PowerPoint 가 실행 중이라 검사하지 않음 — 닫은 뒤 다시 실행"}'
    exit 2
}
$Pptx = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Pptx)     # COM 은 절대 경로만 받는다
if ($OutDir) { $OutDir = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($OutDir) }
$FOOT = 498.0   # 바닥글 선 (6.92in)
$TOL = 1.5
$issues = New-Object System.Collections.Generic.List[string]
$app = New-Object -ComObject PowerPoint.Application
try {
    $pres = $app.Presentations.Open((Resolve-Path $Pptx).Path, -1, 0, 0)
    try {
        $SWp = $pres.PageSetup.SlideWidth; $SHp = $pres.PageSetup.SlideHeight
        if ($OutDir) { New-Item -ItemType Directory -Force -Path $OutDir | Out-Null }
        foreach ($sl in $pres.Slides) {
            $n = $sl.SlideIndex
            foreach ($sh in $sl.Shapes) {
                $top = $sh.Top; $bottom = $sh.Top + $sh.Height; $right = $sh.Left + $sh.Width
                $isBody = $top -lt ($FOOT - 6)
                if ($sh.HasTable) {
                    if ($isBody -and $bottom -gt $FOOT + $TOL) { $issues.Add("slide $n 표 '$($sh.Name)' 아래 끝 $([math]::Round($bottom,1))pt > 바닥글 $FOOT") }
                    continue
                }
                if ($sh.HasTextFrame -and $sh.TextFrame.HasText) {
                    $tr = $sh.TextFrame.TextRange
                    $tb = $tr.BoundTop + $tr.BoundHeight
                    # 오른쪽은 줄마다 끝 공백을 뺀 폭으로 잰다 (줄 끝 공백이 폭에 들어가 생기는 오탐 방지)
                    $trr = 0
                    for ($li = 1; $li -le $tr.Lines().Count; $li++) {
                        $ln = $tr.Lines($li).TrimText()
                        if ($ln.Length -gt 0) { $trr = [math]::Max($trr, $ln.BoundLeft + $ln.BoundWidth) }
                    }
                    $txt = $tr.Text; if ($txt.Length -gt 24) { $txt = $txt.Substring(0, 24) + "…" }
                    $txt = $txt -replace "[`r`n]", " "
                    if ($tb -gt $bottom + $TOL) { $issues.Add("slide $n 글 넘침(아래 $([math]::Round($tb-$bottom,1))pt) '$txt'") }
                    if ($trr -gt $right + $TOL) { $issues.Add("slide $n 글 넘침(오른쪽 $([math]::Round($trr-$right,1))pt) '$txt'") }
                    if ($isBody -and $tb -gt $FOOT + $TOL) { $issues.Add("slide $n 바닥글 침범 $([math]::Round($tb,1))pt '$txt'") }
                }
                if ($bottom -gt $SHp + $TOL -or $right -gt $SWp + $TOL) { $issues.Add("slide $n 슬라이드 밖 '$($sh.Name)'") }
            }
            if ($OutDir) { $sl.Export((Join-Path $OutDir ("slide_{0:D2}.png" -f $n)), "PNG", 1600, 900) }
        }
        $out = [ordered]@{ slides = $pres.Slides.Count; issues = @($issues) }
        $out | ConvertTo-Json -Depth 3
    } finally {
        $pres.Close()
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($pres)
    }
} finally {
    $app.Quit()
    [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($app)
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
    for ($i = 0; $i -lt 30 -and (Get-Process POWERPNT -ErrorAction SilentlyContinue); $i++) { Start-Sleep -Milliseconds 500 }
}
