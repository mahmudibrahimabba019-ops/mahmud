const PRODUCT_DETAILS = {
  37: {
    description: "Bold, smoky, and perfectly spiced. A classic yaji blend made for grilled meats, chicken, and bold flavors.",
    howToUse: "Sprinkle or rub onto meats before or after grilling. Perfect for suya, kebabs, fries, and bold everyday meals.",
    sizes: [
      { weight: "150g", price: 2500, variantId: 37 },
      { weight: "400g", price: 6500, variantId: 40 }
    ]
  },
  38: {
    description: "Bold, smoky yaji with rich daddawa depth. Made for suya and lovers of deep, savory flavor.",
    howToUse: "Sprinkle or rub onto grilled meats and suya. Use sparingly as a finishing spice for bold dishes.",
    sizes: [
      { weight: "150g", price: 2500, variantId: 38 },
      { weight: "400g", price: 7000, variantId: 41 }
    ]
  },
  39: {
    description: "Smoky yaji infused with rich garlic flavor. Bold, aromatic, and perfect for everyday grilling.",
    howToUse: "Sprinkle or rub onto meats before or after grilling. Great for suya, chicken, fish, and roasted vegetables.",
    sizes: [
      { weight: "150g", price: 3000, variantId: 39 },
      { weight: "400g", price: 7000, variantId: 42 }
    ]
  },
  40: {
    // 400g All spice Yaji - same as 37
    description: "Bold, smoky, and perfectly spiced. A classic yaji blend made for grilled meats, chicken, and bold flavors.",
    howToUse: "Sprinkle or rub onto meats before or after grilling. Perfect for suya, kebabs, fries, and bold everyday meals.",
    sizes: [
      { weight: "150g", price: 2500, variantId: 37 },
      { weight: "400g", price: 6500, variantId: 40 }
    ]
  },
  41: {
    // 400g Daddawa Yaji - same as 38
    description: "Bold, smoky yaji with rich daddawa depth. Made for suya and lovers of deep, savory flavor.",
    howToUse: "Sprinkle or rub onto grilled meats and suya. Use sparingly as a finishing spice for bold dishes.",
    sizes: [
      { weight: "150g", price: 2500, variantId: 38 },
      { weight: "400g", price: 7000, variantId: 41 }
    ]
  },
  42: {
    // 400g Garlic Yaji - same as 39
    description: "Smoky yaji infused with rich garlic flavor. Bold, aromatic, and perfect for everyday grilling.",
    howToUse: "Sprinkle or rub onto meats before or after grilling. Great for suya, chicken, fish, and roasted vegetables.",
    sizes: [
      { weight: "150g", price: 3000, variantId: 39 },
      { weight: "400g", price: 7000, variantId: 42 }
    ]
  },
  // Single-size products
  1: { description: "Warm, aromatic spice with notes of clove, cinnamon, and nutmeg. Adds depth and richness to both savory and sweet dishes.", howToUse: "Use in stews, marinades, rice dishes, and baked goods. A little goes a long way.", sizes: [{ weight: "100g", price: 8000, variantId: 1 }] },
  29: { description: "Light, fragrant herb with a fresh, slightly sweet flavor. Perfect for adding brightness to everyday cooking.", howToUse: "Use in sauces, soups, marinades, and vegetable dishes. Great with chicken, fish, and tomato-based meals.", sizes: [{ weight: "50g", price: 1400, variantId: 29 }] },
  30: { description: "Fragrant dried leaves that add deep, earthy flavor to slow-cooked dishes.", howToUse: "Add whole leaves to soups, stews, sauces, and rice while cooking. Remove before serving.", sizes: [{ weight: "50g", price: 1500, variantId: 30 }] },
  2: { description: "Premium black pepper with a bold, aromatic flavor that enhances meats, soups, sauces, and vegetables.", howToUse: "Sprinkle into marinades, soups, stir-fries, grilled meats, or eggs.", sizes: [{ weight: "100g", price: 4000, variantId: 2 }] },
  3: { description: "Whole black peppercorns with a bold, sharp flavor and rich aroma. Perfect for freshly grinding.", howToUse: "Grind fresh over meats, soups, salads, eggs, and sauces, or add whole to stews and stocks.", sizes: [{ weight: "50g", price: 2000, variantId: 3 }] },
  4: { description: "A fragrant spice with a warm, slightly sweet flavor and floral aroma. Used in both savory and sweet dishes.", howToUse: "Add whole pods or ground to rice dishes, teas, baked goods, desserts, and spice blends.", sizes: [{ weight: "50g", price: 7000, variantId: 4 }] },
  5: { description: "A vibrant red pepper powder that adds heat and depth to your favorite dishes.", howToUse: "Use sparingly in stews, sauces, grilled chicken, seafood, or rice dishes.", sizes: [{ weight: "100g", price: 3500, variantId: 5 }] },
  6: { description: "Nutritious tiny seeds packed with fiber, omega-3, and plant protein. Mild flavor that blends easily.", howToUse: "Add to smoothies, oatmeal, yogurt, cereal, or baked goods. Soak in water or milk to make chia pudding.", sizes: [{ weight: "100g", price: 2000, variantId: 6 }] },
  7: { description: "Crushed dried chili peppers that add bold, spicy heat and vibrant flavor.", howToUse: "Sprinkle over pizza, pasta, noodles, soups, grilled meats, vegetables, or stir into sauces.", sizes: [{ weight: "50g", price: 3000, variantId: 7 }] },
  9: { description: "Sweet and fragrant spice perfect for both sweet and savory recipes.", howToUse: "Add to baked goods, oatmeal, smoothies, rice dishes, or sprinkle into tea and coffee.", sizes: [{ weight: "100g", price: 6000, variantId: 9 }] },
  10: { description: "Whole cinnamon sticks with a warm, sweet aroma that adds rich flavor.", howToUse: "Add to teas, rice dishes, stews, desserts, or simmer in drinks. Remove before serving.", sizes: [{ weight: "50g", price: 3000, variantId: 10 }] },
  11: { description: "Strong, aromatic spice with a warm flavor commonly used in cooking and baking.", howToUse: "Add whole or ground to rice dishes, stews, baked goods, and spice blends.", sizes: [{ weight: "50g", price: 3000, variantId: 11 }] },
  12: { description: "A warm, citrusy spice that adds depth and fragrance to many cuisines.", howToUse: "Add to spice blends, curries, roasted vegetables, and marinades.", sizes: [{ weight: "100g", price: 2000, variantId: 12 }] },
  13: { description: "Aromatic seeds with a warm, earthy flavor that add depth and richness to dishes.", howToUse: "Toast lightly to release flavor, then add to curries, rice dishes, soups, and stews.", sizes: [{ weight: "50g", price: 3000, variantId: 13 }] },
  14: { description: "Aromatic seeds with a mild, sweet, licorice-like flavor that add warmth and fragrance.", howToUse: "Add to spice blends, curries, soups, roasted vegetables, or steep in hot water for tea.", sizes: [{ weight: "100g", price: 2000, variantId: 14 }] },
  15: { description: "Aromatic seeds with a slightly bitter, nutty flavor that add depth to traditional dishes.", howToUse: "Use whole or ground in curries, stews, sauces, and spice blends. Toast lightly before adding.", sizes: [{ weight: "100g", price: 1500, variantId: 15 }] },
  16: { description: "Small nutrient-rich seeds packed with fiber, omega-3, and plant protein. Mild nutty flavor.", howToUse: "Add to smoothies, oatmeal, yogurt, cereal, baked goods, or sprinkle over salads.", sizes: [{ weight: "100g", price: 2500, variantId: 16 }] },
  17: { description: "Finely ground garlic that delivers rich flavor without peeling fresh garlic.", howToUse: "Add to marinades, sauces, roasted vegetables, meat rubs, and soups.", sizes: [{ weight: "100g", price: 2500, variantId: 17 }] },
  18: { description: "Warm and aromatic ground ginger that adds a slightly sweet and spicy flavor.", howToUse: "Use in marinades, tea, baked goods, soups, and meat seasoning.", sizes: [{ weight: "100g", price: 2500, variantId: 18 }] },
  31: { description: "A fragrant herb with a fresh citrus aroma that adds bright, refreshing flavor.", howToUse: "Add to soups, stews, marinades, curries, or steep in hot water for tea.", sizes: [{ weight: "50g", price: 1200, variantId: 31 }] },
  32: { description: "A refreshing herb with a cool, aromatic flavor that enhances savory dishes and drinks.", howToUse: "Add to teas, yogurt sauces, salads, smoothies, or sprinkle over rice and grilled meats.", sizes: [{ weight: "50g", price: 1500, variantId: 32 }] },
  19: { description: "A traditional West African spice with a smoky, slightly bitter flavor used in soups.", howToUse: "Add whole to soups, stews, and broths during cooking, then remove before serving.", sizes: [{ weight: "50g", price: 2000, variantId: 19 }] },
  20: { description: "A rich and slightly sweet spice that enhances both sweet and savory dishes.", howToUse: "Sprinkle into baked goods, creamy sauces, soups, and beverages.", sizes: [{ weight: "50g", price: 4000, variantId: 20 }] },
  33: { description: "A fragrant herb with a slightly earthy and peppery flavor, used in many savory dishes.", howToUse: "Add to sauces, marinades, grilled meats, roasted vegetables, pizza, and pasta.", sizes: [{ weight: "50g", price: 2500, variantId: 33 }] },
  21: { description: "A vibrant red spice made from dried peppers, known for mild sweetness and rich color.", howToUse: "Season meats, chicken, fish, soups, rice dishes, and sauces.", sizes: [{ weight: "100g", price: 3000, variantId: 21 }] },
  34: { description: "A fresh-tasting herb with a mild, slightly peppery flavor that enhances many dishes.", howToUse: "Sprinkle over soups, salads, rice, pasta, vegetables, and grilled meats.", sizes: [{ weight: "50g", price: 1500, variantId: 34 }] },
  35: { description: "A fragrant herb with a strong, earthy aroma that adds rich flavor to savory dishes.", howToUse: "Add to roasted meats, chicken, potatoes, vegetables, and marinades.", sizes: [{ weight: "50g", price: 2500, variantId: 35 }] },
  22: { description: "A premium spice known for delicate aroma, golden color, and unique flavor.", howToUse: "Soak a few strands in warm water or milk, then add to rice dishes, soups, sauces, and desserts.", sizes: [{ weight: "50g", price: 3500, variantId: 22 }] },
  23: { description: "Natural sea salt that enhances food flavor with a clean, balanced taste.", howToUse: "Season meats, vegetables, soups, sauces, and everyday cooking.", sizes: [{ weight: "100g", price: 1500, variantId: 23 }] },
  24: { description: "Small seeds with a mild, nutty flavor that add texture and richness.", howToUse: "Sprinkle over salads, stir-fries, noodles, baked goods, or toast and add to rice dishes.", sizes: [{ weight: "50g", price: 3000, variantId: 24 }] },
  25: { description: "A star-shaped spice with a strong, sweet licorice-like flavor used in savory and sweet recipes.", howToUse: "Add whole to soups, stews, broths, teas, and rice dishes, then remove before serving.", sizes: [{ weight: "50g", price: 1500, variantId: 25 }] },
  36: { description: "A fragrant herb with a warm, slightly earthy flavor that enhances savory dishes.", howToUse: "Add to soups, stews, roasted meats, vegetables, marinades, and sauces.", sizes: [{ weight: "50g", price: 2500, variantId: 36 }] },
  26: { description: "A vibrant golden spice known for warm, earthy flavor and natural color.", howToUse: "Add to rice, soups, stews, curries, and marinades.", sizes: [{ weight: "100g", price: 2500, variantId: 26 }] },
  27: { description: "A finely ground spice with mild, smooth heat and subtle flavor, perfect for light-colored dishes.", howToUse: "Season soups, sauces, mashed potatoes, eggs, seafood, and creamy dishes.", sizes: [{ weight: "50g", price: 6500, variantId: 27 }] },
  28: { description: "Whole white peppercorns with mild heat and slightly earthy flavor, ideal for grinding.", howToUse: "Grind fresh over soups, sauces, seafood, vegetables, and light-colored dishes.", sizes: [{ weight: "50g", price: 3500, variantId: 28 }] }
};

export default PRODUCT_DETAILS;
