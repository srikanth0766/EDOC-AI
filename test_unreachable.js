// Test file for JavaScript unreachable code detection

function calculate() {
    const x = 10;
    return x + 20;
    console.log("This line will never execute");
    const y = 5; // Also unreachable
}

calculate();
