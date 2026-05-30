const form = document.getElementById("financeForm");
const resultBox = document.getElementById("resultBox");
const reasonList = document.getElementById("reasonList");
const stepList = document.getElementById("stepList");
const debtPercent = document.getElementById("debtPercent");
const moneyLeft = document.getElementById("moneyLeft");

function valueOf(id) {
    return Number(document.getElementById(id).value);
}

function getFormValues() {
    return {
        monthly_income: valueOf("monthly_income"),
        monthly_expenses: valueOf("monthly_expenses"),
        monthly_debt_payments: valueOf("monthly_debt_payments"),
        credit_score: valueOf("credit_score"),
        missed_payments_12m: valueOf("missed_payments_12m"),
        emergency_savings_months: valueOf("emergency_savings_months")
    };
}

function listItems(items, fallback) {
    if (!items || items.length === 0) {
        return `<li>${fallback}</li>`;
    }

    return items.map(item => `<li>${item.message || item}</li>`).join("");
}

function boxClass(level) {
    if (level === "Good position") {
        return "result-box good";
    }

    if (level === "Needs attention") {
        return "result-box attention";
    }

    return "result-box concern";
}

function showResult(data) {
    resultBox.className = boxClass(data.result.level);
    resultBox.innerHTML = `
        <strong>${data.result.level}</strong>
        <span>${data.result.message}</span>
    `;

    debtPercent.textContent = `${data.numbers.debt_percent}% of income`;
    moneyLeft.textContent = `${data.numbers.money_left}`;

    const reasons = data.reasons.length > 0 ? data.reasons : data.positive_points;
    reasonList.innerHTML = listItems(reasons, "No major concern found.");
    stepList.innerHTML = listItems(data.next_steps, "Keep the current position stable.");
}

function showError(message) {
    resultBox.className = "result-box error";
    resultBox.innerHTML = `<strong>Please check the form</strong><span>${message}</span>`;
    reasonList.innerHTML = "<li>No result shown.</li>";
    stepList.innerHTML = "<li>Fix the form values and try again.</li>";
}

form.addEventListener("submit", async function (event) {
    event.preventDefault();

    try {
        const response = await fetch("/api/evaluate", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(getFormValues())
        });

        const data = await response.json();

        if (response.status === 401) {
            window.location.href = "/login";
            return;
        }

        if (!response.ok) {
            showError(data.message || "Please check the entered values.");
            return;
        }

        showResult(data);
    } catch (error) {
        showError("The result could not be shown. Please try again.");
    }
});
