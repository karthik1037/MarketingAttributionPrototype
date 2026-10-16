
document.addEventListener("DOMContentLoaded", () => {
    const PRICE = 11.99;
    const SAMPLER_PRICE = 29.99;

    const products = [
        "Smoked Habanero",
        "Mango Scorpion",
        "Garlic Jalapeño",
        "Chipotle Honey"
    ];

    let cart = [];

    // Create shopping cart panel
    const panel = document.createElement("aside");
    panel.id = "cart-panel";
    panel.className = "cart-panel";
    panel.hidden = true;

    panel.innerHTML = `
        <h2>Your Cart</h2>
        <div id="cart-items"></div>
        <h3 id="cart-total">Total: $0.00</h3>
        <button id="checkout-btn" type="button">
            Simulate Checkout
        </button>
        <button id="close-cart" type="button">
            Close
        </button>
    `;

    document.body.appendChild(panel);

    function updateCart() {
        const count = cart.length;
        document.querySelector(".cart span").textContent = count;

        const items = document.getElementById("cart-items");
        items.replaceChildren();

        let total = 0;

        cart.forEach(item => {
            total += item.price;

            const row = document.createElement("p");
            row.textContent =
                `${item.name} — $${item.price.toFixed(2)}`;
            items.appendChild(row);
        });

        document.getElementById("cart-total").textContent =
            `Total: $${total.toFixed(2)}`;
    }

    function addToCart(name, price) {
        cart.push({ name, price });
        updateCart();
        panel.hidden = false;
    }

    // Shop all sauces
    document.getElementById("shop-btn")
        .addEventListener("click", () => {
            document.getElementById("products")
                .scrollIntoView({ behavior: "smooth" });
        });

    // Three-bottle sampler
    document.getElementById("sampler-btn")
        .addEventListener("click", () => {
            addToCart("3-Pack Sampler", SAMPLER_PRICE);
        });

    // Product add-to-cart buttons
    document.querySelectorAll(".prod .add")
        .forEach((button, index) => {
            button.setAttribute("role", "button");
            button.setAttribute("tabindex", "0");

            const addProduct = () => {
                addToCart(products[index], PRICE);
            };

            button.addEventListener("click", addProduct);
            button.addEventListener("keydown", event => {
                if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    addProduct();
                }
            });
        });

    // Open cart
    const cartButton = document.querySelector(".cart");
    cartButton.setAttribute("role", "button");
    cartButton.setAttribute("tabindex", "0");

    cartButton.addEventListener("click", () => {
        panel.hidden = false;
    });

    cartButton.addEventListener("keydown", event => {
        if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            panel.hidden = false;
        }
    });

    document.getElementById("close-cart")
        .addEventListener("click", () => {
            panel.hidden = true;
        });

    // Demo checkout only
    document.getElementById("checkout-btn")
    .addEventListener("click", async () => {

        if (cart.length === 0) {
            alert("Your cart is empty.");
            return;
        }

        const checkoutButton =
            document.getElementById("checkout-btn");

        checkoutButton.disabled = true;

        try {
            const response = await fetch("/checkout", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    items: cart.map(item => ({
                        name: item.name
                    }))
                })
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(
                    result.error || "Checkout failed."
                );
            }

            alert(
                `Order #${result.order_id} saved!\n` +
                `Total: $${result.total.toFixed(2)}\n` +
                `This was a simulated purchase.`
            );

            cart = [];
            updateCart();
            panel.hidden = true;

        } catch (error) {
            alert(error.message);
        } finally {
            checkoutButton.disabled = false;
        }
    });

    // Allow customer to select survey answer
    document.querySelectorAll(".opt").forEach(option => {
        option.setAttribute("role", "radio");
        option.setAttribute("tabindex", "0");

        const selectOption = () => {
            document.querySelectorAll(".opt")
                .forEach(item => {
                    item.classList.remove("on");
                    item.setAttribute("aria-checked", "false");
                });

            option.classList.add("on");
            option.setAttribute("aria-checked", "true");
        };

        option.addEventListener("click", selectOption);
        option.addEventListener("keydown", event => {
            if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                selectOption();
            }
        });
    });

    updateCart();
});
