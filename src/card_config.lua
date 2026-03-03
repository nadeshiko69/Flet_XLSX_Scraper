-- card_config.lua
-- Cardの共通情報を定義
local card_config = {}

local ranks = {
    [1] = "A",
    [2] = "2",
    [3] = "3",
    [4] = "4",
    [5] = "5",
    [6] = "6",
    [7] = "7",
    [8] = "8",
    [9] = "9",
    [10] = "10",
    [11] = "J",
    [12] = "Q",
    [13] = "K"
}
local suits = { "Hearts", "Diamonds", "Clubs", "Spades" }


function card_config.get_card_info(id)
    assert(type(id) == "number", "id must be a number")
    assert(id >= 0 and id <= 52, "id must be in range [0, 52]")

    if id == 0 then
        -- Joker
        local info = { id = 0, label = "Joker" }
        print("Card: Joker")
        return info
    end

    -- 1..13:Hearts, 14..26:Diamonds, 27..39:Clubs, 40..52:Spades
    local suitIndex = math.ceil(id / 13)                -- 1..4
    local rankIndex = ((id - 1) % 13) + 1               -- 1..13

    local suit = suits[suitIndex]
    local rank = ranks[rankIndex]
    local label = string.format("%s %s", suit, rank)

    print("Card: " .. label)
    return { id = id, suit = suit, rank = rank, label = label }
end



return card_config