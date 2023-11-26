karel_assgnids = [2023, "2023", "checkerboard", "diagnostic3", "diagnostic3soln", "fillkarel", "hospital", "housekarel", "jigsaw", "midpoint", "mountain", "warmup", "steeplechase", "stepup", "stonemason", "spreadbeepers", "rhoomba", "randompainter", "outline", "piles", 
                  "es-karel-midpoint", "es-karel-cone-pile", "es-karel-stripe", "es-karel-collect-newspaper", "es-karel-hospital", "es-karel-stone-mason", "es-karel-mountain", "es-karel-beeper-line", "es-karel-jump-up", "es-karel-hurdle", "es-karel-checkerboard", 
                  "es-karel-step-up", "es-karel-dog-years", "es-karel-place-2023", "es-karel-mystery", "es-karel-invert-beeper-1d", "es-karel-un", "es-karel-random-painting", "es-karel-outline", "es-karel-fill", "es-karel-to-the-wall", "es-project-karel", "es-karel-place-100",
                  "es-karel-big-beeper", "karelflag", 'movebeeper', 'diamond', 'place10beepers', 'zigzag']

def not_karel(row):
    return row['assnId'] not in karel_assgnids and row['type'] != 'karel'