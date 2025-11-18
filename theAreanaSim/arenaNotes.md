# "medkit" 
Custom use text 

# "snare trap"
Custom Use Text 

# "flare"
Custom Use Text

# "throwing knife"
Custom Use Text

# "Taco Bell Meal Deal"
Custom Loot Text
Custom Use Text

# "herb bundle"
Custom Loot Text

# Bow
Custom Use Text

# Stick
Custom use text

# poetry anthology
Custom use text 
custom loot text 

### GENERIC ITEMS
# "camouflage cloak"
# "ration pack"
# dagger
# steel bar
# cheese wheel

---

## Template Examples

- **Multi-person non-lethal**  
  ```text
  {person} plots quietly with {ally} and {rival} deep into the night.
  ```
  Use `extra_roles: ["ally", "rival"]` to ensure two unique tributes are pulled into the scene.

- **Multi-victim lethal**  
  ```text
  {killer} launches explosives that wipe out {victim} and {victim2}.
  ```
  Attach `"victim_count": 2` (or more) to any lethal template to eliminate multiple tributes at once.

- **Special item event with per-entry consumption**  
  ```json
  {
      "text": "{person} rains arrows until {victim} and {victim2} both drop.",
      "lethal": true,
      "victim_count": 2,
      "consumes": true
  }
  ```
  Even if the item’s default `consumes` flag is false, you can override consumption per event while also defining how many victims it targets.



### TO - DO

add taco bell breakfast 
 - no lethal abilities 

Add some nonlethal events for the novelty sunglasses

Make there a chance to have the muddy water kill you

Chopsticks
 - some lethal some non lethal, lethal consumes

team of navy seals
 - lethal event

ramen
 - nonlethal consumes 

Recieving an item from Temu instead of a sponsor 

reinforcing a shelter event can also collapse and kill the player 

add "Wii Sports (Nintendo Wii, 2007) New Game Factory Sealed in Cardboard Sleeve" to the game 
 - lethal non consuming, more monlethal flavor text than lethal texts

