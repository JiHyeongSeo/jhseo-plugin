-- cs 단축키 가이드를 status line 중앙에 표시
-- order: 기존 LEFT 항목들(mode=1000, size=2000, name=3000) 이후에 오도록 큰 값 사용
Status:children_add(function()
    return ui.Line({
        ui.Span("  "),
        ui.Span("^S"):fg("yellow"):bold(),
        ui.Span(":세션 "),
        ui.Span("^N"):fg("yellow"):bold(),
        ui.Span(":새세션 "),
        ui.Span("^J"):fg("yellow"):bold(),
        ui.Span(":이동 "),
        ui.Span("^G"):fg("yellow"):bold(),
        ui.Span(":git "),
        ui.Span("^F"):fg("yellow"):bold(),
        ui.Span(":찾기 "),
        ui.Span("^Q"):fg("yellow"):bold(),
        ui.Span(":종료"),
    })
end, 8000, Status.LEFT)
