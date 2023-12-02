function get_sum(input::String)::Int
    re = r"[0-9]"
    lines = split(input, "\n")
    first_digit = map(x ->  x.match, filter(x -> ~isnothing(x), map(x-> match(re, x), lines)))
    second_digit = map(x -> x.match, filter(x -> ~isnothing(x), map(x-> match(re, reverse(x)), lines))) 
    return sum(map((a, b) -> parse(Int, a * b), first_digit, second_digit))
end

function match_all_with_overlapping(pattern::Regex, input::AbstractString)::Union{Tuple{String,String}, Nothing}
    m = match(pattern, input)
    first = last = m.match
    while ~isnothing(m)
        last = m.match
        m = match(pattern, input, m.offset + 1)
    end
    return first, last
end

function get_line_value(pattern::Regex, line::AbstractString, mapping:: Dict{String, String})::Int 
    a, b = match_all_with_overlapping(pattern, line)
    return parse(Int, get!(mapping, a, a) * get!(mapping, b, b))
end


function get_sum_with_strings(input::String)::Int
    mapping = Dict("one"=>"1", "two"=>"2", "three"=>"3", "four"=>"4", "five"=>"5",
                "six"=>"6", "seven"=>"7", "eight"=>"8", "nine"=>"9")
    pattern = Regex("[1-9]|" * join(keys(mapping), "|"))
    return sum(map(x -> get_line_value(pattern, x, mapping), 
                eachsplit(input, "\n", keepempty=false)))     
end


input = read(joinpath(@__DIR__, "input.txt"), String)
@time result = get_sum(input)
println(result)
input = read(joinpath(@__DIR__, "input.txt"), String)
@time result = get_sum_with_strings(input)
println(result)

