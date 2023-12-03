function parse_line(line::String, pattern::Regex)::Dict{String,Int}
    values = Dict{String,Int}()
    _, extraction_lines = split(line, ":")
    for extraction_line in split(extraction_lines, ";")
        for color_extraction in split(extraction_line, ",")
            value, color = match(pattern, color_extraction).captures
            value = parse(Int, value)
            if value > get!(values, color, 0)
                values[color] = value
            end
        end
    end
    return values
end


function find_valid(input_path::String)::Int
    pattern = Regex("([0-9]+) (green|blue|red)")
    allowed_maxima = Dict{String,Int}(
        "red" => 12, "green" => 13, "blue" => 14
    )
    maxima = map(x -> parse_line(x, pattern), eachline(input_path))
    valid = map(x -> all(key -> x[key] <= allowed_maxima[key], collect(keys(x))), maxima)
    return sum(map(val -> val[1] * val[2], enumerate(valid)))
end

function find_power(input_path::String)::Int
    pattern = Regex("([0-9]+) (green|blue|red)")
    maxima = map(x -> parse_line(x, pattern), eachline(input_path))
    return sum(map(x -> reduce((a, b) -> a * b, collect(values(x))), maxima))
end

@time result = find_valid(joinpath(@__DIR__, "input.txt"))
println(result)

@time result = find_power(joinpath(@__DIR__, "input.txt"))
println(result)