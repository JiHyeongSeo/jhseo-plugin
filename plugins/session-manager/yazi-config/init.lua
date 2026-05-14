-- cs 단축키 가이드를 status line에 표시
Status:children_add(function()
    return ui.Line({
        ui.Span(" "),
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
        ui.Span(":종료 "),
        ui.Span("^Z"):fg("yellow"):bold(),
        ui.Span(":detach"),
    })
end, 500, Status.LEFT)
