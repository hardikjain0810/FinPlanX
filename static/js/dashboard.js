document.addEventListener('DOMContentLoaded', function() {
    // Navigation between sections
    const menuItems = document.querySelectorAll('.sidebar-menu li');
    const sections = document.querySelectorAll('.content-section');
    
    menuItems.forEach(item => {
        item.addEventListener('click', function() {
            const sectionId = this.getAttribute('data-section');
            
            // Remove active class from all menu items and sections
            menuItems.forEach(item => item.classList.remove('active'));
            sections.forEach(section => section.classList.remove('active'));
            
            // Add active class to clicked menu item and corresponding section
            this.classList.add('active');
            document.getElementById(sectionId).classList.add('active');
        });
    });
    
    // Prediction form handling
    const predictionForm = document.getElementById('predictionForm');
    const resultsContainer = document.getElementById('results-container');
    
    if (predictionForm) {
        predictionForm.addEventListener('submit', function(e) {
            e.preventDefault(); // Prevent the form from submitting normally
            
            const investmentAmount = document.getElementById('investment_amount').value;
            const riskTolerance = document.getElementById('risk_tolerance').value;
            const investmentPeriod = document.getElementById('investment_period').value;
            
            // Show loading state
            const submitButton = this.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.textContent;
            submitButton.textContent = 'Processing...';
            submitButton.disabled = true;
            
            // Prepare data for API call
            const data = {
                investment_amount: investmentAmount,
                risk_tolerance: riskTolerance,
                investment_period: investmentPeriod
            };
            
            console.log('Sending prediction request with data:', data);
            
            // Make API call to get predictions
            fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
                credentials: 'same-origin'
            })
            .then(response => {
                console.log('Received response status:', response.status);
                if (!response.ok) {
                    throw new Error('Network response was not ok: ' + response.status);
                }
                return response.json().catch(err => {
                    console.error('Error parsing JSON:', err);
                    throw new Error('Failed to parse response as JSON');
                });
            })
            .then(data => {
                console.log('Prediction data received:', JSON.stringify(data, null, 2));
                
                // Validate the data structure
                if (!data || !data.predicted_returns || !data.recommendations) {
                    console.error('Invalid data structure received:', data);
                    throw new Error('Invalid data structure received from server');
                }
                
                // Reset button state
                submitButton.textContent = originalButtonText;
                submitButton.disabled = false;
                
                try {
                    // Display results
                    displayResults(data);
                    
                    // Store the current prediction for saving later
                    window.currentPrediction = {
                        investment_amount: investmentAmount,
                        risk_tolerance: riskTolerance,
                        investment_period: investmentPeriod,
                        predicted_returns: data.predicted_returns,
                        recommendations: data.recommendations
                    };
                } catch (displayError) {
                    console.error('Error displaying results:', displayError);
                    alert('Error displaying results: ' + displayError.message);
                }
            })
            .catch(error => {
                console.error('Error in prediction process:', error);
                submitButton.textContent = originalButtonText;
                submitButton.disabled = false;
                alert('An error occurred: ' + error.message);
            });
        });
    }
    
    // Save button handling
    const saveButton = document.getElementById('saveButton');
    if (saveButton) {
        saveButton.addEventListener('click', function() {
            if (!window.currentPrediction) {
                alert('No prediction to save. Please make a prediction first.');
                return;
            }
            
            // Show loading state
            const originalButtonText = this.textContent;
            this.textContent = 'Saving...';
            this.disabled = true;
            
            // Make API call to save the plan
            fetch('/save-plan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(window.currentPrediction),
                credentials: 'same-origin'
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Reset button state
                this.textContent = originalButtonText;
                this.disabled = false;
                
                alert('Plan saved successfully!');
            })
            .catch(error => {
                console.error('Error:', error);
                this.textContent = originalButtonText;
                this.disabled = false;
                alert('An error occurred while saving your plan. Please try again.');
            });
        });
    }
    
    // Load saved plans when the saved plans section is clicked
    const savedPlansMenuItem = document.querySelector('.sidebar-menu li[data-section="saved-plans-section"]');
    if (savedPlansMenuItem) {
        savedPlansMenuItem.addEventListener('click', loadSavedPlans);
    }
    
    // Function to display prediction results
    function displayResults(data) {
        console.log('Starting to display results with data:', JSON.stringify(data, null, 2));
        
        try {
            // Update summary values with rupee symbol
            document.getElementById('initialInvestment').textContent = '₹' + parseFloat(data.predicted_returns.initial_investment).toLocaleString();
            document.getElementById('returnRate').textContent = data.predicted_returns.predicted_return_rate + '%';
            document.getElementById('finalValue').textContent = '₹' + parseFloat(data.predicted_returns.final_value).toLocaleString();
            document.getElementById('totalGrowth').textContent = data.predicted_returns.total_growth + '%';
            
            // Create growth chart
            if (Array.isArray(data.predicted_returns.annual_returns)) {
                createGrowthChart(data.predicted_returns.annual_returns);
            } else {
                console.error('annual_returns is not an array:', data.predicted_returns.annual_returns);
                throw new Error('Invalid annual_returns data');
            }
            
            // Create allocation chart
            if (data.recommendations && data.recommendations.asset_allocation) {
                createAllocationChart(data.recommendations.asset_allocation);
            } else {
                console.error('asset_allocation is missing or invalid:', data.recommendations);
                throw new Error('Invalid asset_allocation data');
            }
            
            // Populate recommendations table
            if (Array.isArray(data.recommendations.specific_investments)) {
                populateRecommendationsTable(data.recommendations.specific_investments);
            } else {
                console.error('specific_investments is not an array:', data.recommendations.specific_investments);
                throw new Error('Invalid specific_investments data');
            }
            
            // Show results container
            resultsContainer.classList.remove('hidden');
            console.log('Results displayed successfully');
        } catch (error) {
            console.error('Error in displayResults:', error);
            throw new Error('Failed to display results: ' + error.message);
        }
    }
    
    // Function to create growth chart
    function createGrowthChart(annualReturns) {
        const ctx = document.getElementById('growthChart').getContext('2d');
        
        // Properly check and destroy existing chart
        if (window.growthChart instanceof Chart) {
            window.growthChart.destroy();
        }
        
        const years = annualReturns.map(item => 'Year ' + item.year);
        const values = annualReturns.map(item => item.value);
        
        window.growthChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: years,
                datasets: [{
                    label: 'Investment Value',
                    data: values,
                    backgroundColor: 'rgba(108, 92, 231, 0.2)',
                    borderColor: 'rgba(108, 92, 231, 1)',
                    borderWidth: 2,
                    pointBackgroundColor: 'rgba(0, 206, 201, 1)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: 'rgba(220, 221, 225, 0.8)',
                            callback: function(value) {
                                return '₹' + value.toLocaleString();
                            }
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: 'rgba(220, 221, 225, 0.8)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            color: 'rgba(220, 221, 225, 0.8)'
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return '₹' + context.parsed.y.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Function to create allocation chart
    function createAllocationChart(assetAllocation) {
        const ctx = document.getElementById('allocationChart').getContext('2d');
        
        // Properly check and destroy existing chart
        if (window.allocationChart instanceof Chart) {
            window.allocationChart.destroy();
        }
        
        const labels = Object.keys(assetAllocation);
        const data = Object.values(assetAllocation);
        
        // Generate colors for each segment
        const colors = [
            'rgba(108, 92, 231, 0.8)',
            'rgba(0, 206, 201, 0.8)',
            'rgba(253, 203, 110, 0.8)',
            'rgba(225, 112, 85, 0.8)',
            'rgba(0, 184, 148, 0.8)'
        ];
        
        window.allocationChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors,
                    borderColor: 'rgba(45, 52, 54, 0.5)',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            color: 'rgba(220, 221, 225, 0.8)',
                            padding: 15,
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.parsed + '%';
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Function to populate recommendations table
    function populateRecommendationsTable(investments) {
        const tableBody = document.querySelector('#recommendationsTable tbody');
        tableBody.innerHTML = '';
        
        investments.forEach(investment => {
            const row = document.createElement('tr');
            
            const nameCell = document.createElement('td');
            nameCell.textContent = investment.name;
            
            const allocationCell = document.createElement('td');
            allocationCell.textContent = investment.percentage + '%';
            
            const returnCell = document.createElement('td');
            returnCell.textContent = investment.expected_return + '%';
            
            row.appendChild(nameCell);
            row.appendChild(allocationCell);
            row.appendChild(returnCell);
            
            tableBody.appendChild(row);
        });
    }
    
    // Function to load saved plans
    function loadSavedPlans() {
        const savedPlansContainer = document.getElementById('savedPlansContainer');
        savedPlansContainer.innerHTML = '<div class="loading">Loading saved plans...</div>';
        
        fetch('/get-plans', {
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            savedPlansContainer.innerHTML = '';
            
            if (data.plans.length === 0) {
                savedPlansContainer.innerHTML = '<div class="no-plans">You have no saved plans. Create a prediction and save it to see it here.</div>';
                return;
            }
            
            data.plans.forEach(plan => {
                const planCard = document.createElement('div');
                planCard.className = 'saved-plan-card';
                planCard.innerHTML = `
                    <div class="saved-plan-header">
                        <h3>Investment Plan</h3>
                        <button class="delete-plan-btn" data-id="${plan.id}">×</button>
                    </div>
                    <div class="saved-plan-details">
                        <p><span>Investment Amount:</span> <span>₹${parseFloat(plan.investment_amount).toLocaleString()}</span></p>
                        <p><span>Risk Level:</span> <span>${getRiskLevelText(plan.risk_tolerance)}</span></p>
                        <p><span>Period:</span> <span>${plan.investment_period} years</span></p>
                        <p><span>Expected Return:</span> <span>${plan.predicted_returns.predicted_return_rate}%</span></p>
                        <p><span>Final Value:</span> <span>₹${parseFloat(plan.predicted_returns.final_value).toLocaleString()}</span></p>
                    </div>
                    <button class="view-details-btn" data-plan='${JSON.stringify(plan)}'>View Details</button>
                `;
                
                savedPlansContainer.appendChild(planCard);
            });
            
            // Add event listeners for delete buttons
            document.querySelectorAll('.delete-plan-btn').forEach(button => {
                button.addEventListener('click', function() {
                    const planId = this.getAttribute('data-id');
                    deletePlan(planId, this.closest('.saved-plan-card'));
                });
            });
            
            // Add event listeners for view details buttons
            document.querySelectorAll('.view-details-btn').forEach(button => {
                button.addEventListener('click', function() {
                    const plan = JSON.parse(this.getAttribute('data-plan'));
                    
                    // Switch to prediction section
                    document.querySelector('.sidebar-menu li[data-section="prediction-section"]').click();
                    
                    // Fill the form with the plan data
                    document.getElementById('investment_amount').value = plan.investment_amount;
                    document.getElementById('risk_tolerance').value = plan.risk_tolerance;
                    document.getElementById('investment_period').value = plan.investment_period;
                    
                    // Display the results
                    const data = {
                        predicted_returns: plan.predicted_returns,
                        recommendations: plan.recommendations
                    };
                    displayResults(data);
                    
                    // Store the current prediction
                    window.currentPrediction = {
                        investment_amount: plan.investment_amount,
                        risk_tolerance: plan.risk_tolerance,
                        investment_period: plan.investment_period,
                        predicted_returns: plan.predicted_returns,
                        recommendations: plan.recommendations
                    };
                });
            });
        })
        .catch(error => {
            console.error('Error:', error);
            savedPlansContainer.innerHTML = '<div class="error">An error occurred while loading your saved plans. Please try again.</div>';
        });
    }
    
    // Function to delete a plan
    function deletePlan(planId, planElement) {
        if (!confirm('Are you sure you want to delete this plan?')) {
            return;
        }
        
        fetch(`/delete-plan/${planId}`, {
            method: 'DELETE',
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Remove the plan card from the DOM
            planElement.remove();
            
            // If no plans left, show message
            if (document.querySelectorAll('.saved-plan-card').length === 0) {
                document.getElementById('savedPlansContainer').innerHTML = 
                    '<div class="no-plans">You have no saved plans. Create a prediction and save it to see it here.</div>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while deleting the plan. Please try again.');
        });
    }
    
    // Helper function to get risk level text
    function getRiskLevelText(riskLevel) {
        const riskLevels = {
            '1': 'Very Conservative',
            '2': 'Conservative',
            '3': 'Moderate',
            '4': 'Aggressive',
            '5': 'Very Aggressive'
        };
        return riskLevels[riskLevel] || 'Unknown';
    }
});