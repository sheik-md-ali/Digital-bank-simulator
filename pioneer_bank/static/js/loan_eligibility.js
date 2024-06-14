$(document).ready(function() {
    // Function to check loan eligibility
    $("#eligibilityForm").submit(function(event) {
      event.preventDefault(); // Prevent form submission
      checkLoanEligibility();
    });
  
    function checkLoanEligibility() {
      // Get values from input fields
      var salary = parseFloat($("#salary").val());
      var creditScore = parseFloat($("#creditScore").val());
      var workExperience = parseFloat($("#workExperience").val());
  
      var result = ""; // Initialize result variable
  
      // Check eligibility criteria
      if (salary >= 50000 && creditScore >= 650 && workExperience >= 6) {
        result = "Congratulations! You're eligible for the loan.";
        // Enable the 'Next' button
        $("#nextButton").prop("disabled", false);
      } else {
        result = "Sorry, you don't meet the eligibility criteria for the loan.";
        // Disable the 'Next' button
        $("#nextButton").prop("disabled", true);
      }
  
      // Display result
      $("#result").text(result);
    }
  
    // Event listener for the clear button
    $("#clear").click(function() {
      // Clear input fields and result
      $("#salary, #creditScore, #workExperience").val("");
      $("#result").text("");
      // Disable the 'Next' button
      $("#nextButton").prop("disabled", true);
    });
  
    // Event listener for the 'Next' button
    $("#nextButton").click(function() {
      // Check eligibility before redirection
      checkLoanEligibility();
      var resultText = $("#result").text();
      if (resultText.includes("Congratulations")) {
        // Redirect to the next page (loan1.html)
        window.location.href = "/loan_application";
      }
    });
  });
  