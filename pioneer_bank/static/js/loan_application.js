window.addEventListener('load', function() {
    // Function to update loan amount display
    function updateLoanAmountDisplay() {
        const loanAmountSelect = document.getElementById('loanAmount');
        const calculatedRate = document.getElementById('calculatedRateValue');
        const loanDuration = parseInt(document.getElementById('loanDuration').value);

        // Get the selected loan amount option value
        const selectedLoanAmountOption = loanAmountSelect.value;
        const loanAmount = parseFloat(selectedLoanAmountOption);

        // Calculate the interest rate based on the loan amount and duration (you can customize this logic)
        let interestRate = 8; // Default 8% interest rate

        // Calculate the total amount to be paid back
        const totalAmount = loanAmount * (1 + (interestRate / 100) * (loanDuration / 12)); // Adjust interest based on loan duration

        // Update displayed loan amount and calculated rate
        calculatedRate.textContent = interestRate.toFixed(2) + '%'; // Display the interest rate

        // Display the total amount
        const totalAmountElement = document.getElementById('totalAmount');
        if (totalAmountElement) {
            totalAmountElement.textContent = totalAmount.toFixed(2);
        }
    }

    // Add event listeners to the loan amount and loan duration dropdowns
    document.getElementById('loanAmount').addEventListener('change', updateLoanAmountDisplay);
    document.getElementById('loanDuration').addEventListener('change', updateLoanAmountDisplay);

    // Initialize the display
    updateLoanAmountDisplay();
});
