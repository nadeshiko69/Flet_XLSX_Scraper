
function compareCards(card1, card2)
    local cardValues = {["2"] = 2, ["3"] = 3, ["4"] = 4, ["5"] = 5, ["6"] = 6, ["7"] = 7, ["8"] = 8, ["9"] = 9, ["10"] = 10, ["J"] = 11, ["Q"] = 12, ["K"] = 13, ["A"] = 14}
    
    local value1 = cardValues[card1]
    local value2 = cardValues[card2]
    
    if value1 == value2 then
        return "It's a tie!"
    elseif (value1 == 2 and value2 == 14) then
        return "Card 1 wins! (2 beats A)"
    elseif (value1 == 14 and value2 == 2) then
        return "Card 2 wins! (A beats 2)"
    elseif value1 > value2 then
        return "Card 1 wins!"
    else
        return "Card 2 wins!"
    end
end


print(compareCards("2", "A")) -- Output: Card 1 wins! (2 beats A)