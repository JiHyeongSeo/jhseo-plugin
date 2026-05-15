-- cs 단축키 가이드 + yazi 기본 키
Status:children_add(function()
    return ui.Line({
        ui.Span("  "),
        -- cs 키
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
        ui.Span("│ "):fg("gray"),
        -- yazi 키
        ui.Span("a"):fg("cyan"):bold(),
        ui.Span(":생성 "),
        ui.Span("r"):fg("cyan"):bold(),
        ui.Span(":이름 "),
        ui.Span("d"):fg("cyan"):bold(),
        ui.Span(":삭제 "),
        ui.Span("y"):fg("cyan"):bold(),
        ui.Span(":복사 "),
        ui.Span("p"):fg("cyan"):bold(),
        ui.Span(":붙여 "),
        ui.Span("x"):fg("cyan"):bold(),
        ui.Span(":잘라 "),
        ui.Span("space"):fg("cyan"):bold(),
        ui.Span(":선택"),
    })
end, 8000, Status.LEFT)

-- bg 세션 카운트 (Status.RIGHT 좌측)
Status:children_add(function()
    local f = io.open("/tmp/cs-counts.txt", "r")
    if not f then return ui.Line("") end
    local content = f:read("*all") or ""
    f:close()
    local bg = content:match("bg=(%d+)") or "0"
    local active = content:match("active=(%d+)") or "0"
    local spans = { ui.Span(" ") }
    if active == "1" then
        table.insert(spans, ui.Span("●"):fg("green"))
        table.insert(spans, ui.Span(" "))
    end
    if tonumber(bg) > 0 then
        table.insert(spans, ui.Span("bg:"):fg("magenta"))
        table.insert(spans, ui.Span(bg):fg("magenta"):bold())
        table.insert(spans, ui.Span(" "))
    end
    return ui.Line(spans)
end, 9000, Status.RIGHT)
