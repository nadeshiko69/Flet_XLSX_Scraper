
local card_conf = require("card_config")

local function create_and_shuffle_deck(min, max)
    local numbers = {}
    for i = min, max do
        table.insert(numbers, i)
    end

    -- Fisher–Yates シャッフル
    math.randomseed(os.time())
    for i = #numbers, 2, -1 do
        local j = math.random(1, i)
        numbers[i], numbers[j] = numbers[j], numbers[i]
    end
    return numbers
end

local function create_initial_hand(deck)
    local hand_player1 = {}
    local hand_player2 = {}

    -- Player 1
    table.insert(hand_player1, table.remove(deck))
    table.insert(hand_player1, table.remove(deck))

    -- Player 2
    table.insert(hand_player2, table.remove(deck))
    table.insert(hand_player2, table.remove(deck))

    return hand_player1, hand_player2
end

local set_card = {}

-- 手札から指定したほうのカードをPopする関数
local function pop_card_from_hand(hand, index)
    assert(index == 1 or index == 2, "index must be 1 or 2")
    return table.remove(hand, index)
end

local function set_card_from_hand(hand, index, player)
    set_card[player] = hand[index]
end

-- Demo
local decks = create_and_shuffle_deck(0, 52)
print(table.concat(decks, ", "))


print("-- Initial Hand --")
local player_hand1, player_hand2 = create_initial_hand(decks)
print("Player 1's hand: " .. table.concat(player_hand1, ", "))
print("Player 2's hand: " .. table.concat(player_hand2, ", "))

print("----")
print("-- set card --")
print("----")
set_card_from_hand(player_hand1, 1, "player1")
pop_card_from_hand(player_hand1, 1)
set_card_from_hand(player_hand2, 2, "player2")
pop_card_from_hand(player_hand2, 2)
print("SET : " .. set_card["player1"] .. " vs " .. set_card["player2"])
print("Player 1's hand: " .. table.concat(player_hand1, ", "))
card_conf.get_card_info(player_hand1[1])
print("Player 2's hand: " .. table.concat(player_hand2, ", "))
card_conf.get_card_info(player_hand2[1])

print("----")
print("-- open card --")
print("----")