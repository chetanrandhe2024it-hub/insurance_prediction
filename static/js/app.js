/**
 * CareCast AI — Frontend Application Logic
 * Streamlined, minimalist dark theme interactions with brand palette.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Inputs
  const form = document.getElementById('prediction-form');
  const ageInput = document.getElementById('age');
  const ageDisplay = document.getElementById('age-display');
  const bmiInput = document.getElementById('bmi');
  const bmiBadge = document.getElementById('bmi-badge');
  const childrenInput = document.getElementById('children');
  const childrenChips = document.querySelectorAll('#children-pills .num-chip');

  // Outputs
  const predictedAnnualEl = document.getElementById('predicted-annual');
  const predictedMonthlyEl = document.getElementById('predicted-monthly');
  const riskTierEl = document.getElementById('risk-tier');
  const factorListEl = document.getElementById('factor-list');
  const btnSubmit = document.getElementById('btn-submit');
  const btnCaption = btnSubmit.querySelector('.btn-caption');
  const btnSpinner = btnSubmit.querySelector('.btn-spinner');

  // Meta stats
  const metaPatient = document.getElementById('meta-patient');
  const metaBmiKids = document.getElementById('meta-bmi-kids');
  const metaRegionSmoker = document.getElementById('meta-region-smoker');

  // Copy & Toast
  const btnCopy = document.getElementById('btn-copy');
  const toast = document.getElementById('toast');

  let currentAnnualCost = 0;

  // -------------------------------------------------------------
  // Age Slider Sync
  // -------------------------------------------------------------
  ageInput.addEventListener('input', (e) => {
    ageDisplay.textContent = `${e.target.value} yrs`;
  });

  // -------------------------------------------------------------
  // BMI Live Badge
  // -------------------------------------------------------------
  function updateBmiBadge(val) {
    const bmi = parseFloat(val);
    if (isNaN(bmi)) return;

    if (bmi < 18.5) {
      bmiBadge.textContent = 'Underweight';
      bmiBadge.style.color = '#a4dad2';
      bmiBadge.style.background = 'rgba(164, 218, 210, 0.12)';
      bmiBadge.style.borderColor = 'rgba(164, 218, 210, 0.3)';
    } else if (bmi <= 24.9) {
      bmiBadge.textContent = 'Normal';
      bmiBadge.style.color = '#bce08a';
      bmiBadge.style.background = 'rgba(188, 224, 138, 0.12)';
      bmiBadge.style.borderColor = 'rgba(188, 224, 138, 0.3)';
    } else if (bmi <= 29.9) {
      bmiBadge.textContent = 'Overweight';
      bmiBadge.style.color = '#f6d809';
      bmiBadge.style.background = 'rgba(246, 216, 9, 0.12)';
      bmiBadge.style.borderColor = 'rgba(246, 216, 9, 0.3)';
    } else {
      bmiBadge.textContent = 'Obese';
      bmiBadge.style.color = '#f6d809';
      bmiBadge.style.background = 'rgba(246, 216, 9, 0.18)';
      bmiBadge.style.borderColor = 'rgba(246, 216, 9, 0.4)';
    }
  }

  bmiInput.addEventListener('input', (e) => updateBmiBadge(e.target.value));
  updateBmiBadge(bmiInput.value);

  // -------------------------------------------------------------
  // Children Chips Selector
  // -------------------------------------------------------------
  childrenChips.forEach((chip) => {
    chip.addEventListener('click', () => {
      childrenChips.forEach((c) => c.classList.remove('active'));
      chip.classList.add('active');
      childrenInput.value = chip.getAttribute('data-val');
    });
  });

  // -------------------------------------------------------------
  // Presets
  // -------------------------------------------------------------
  const presets = {
    young: { age: 22, sex: 'female', bmi: 21.5, children: 0, smoker: 'no', region: 'northwest' },
    family: { age: 38, sex: 'male', bmi: 26.2, children: 2, smoker: 'no', region: 'northeast' },
    smoker: { age: 46, sex: 'male', bmi: 32.5, children: 1, smoker: 'yes', region: 'southeast' },
    senior: { age: 62, sex: 'female', bmi: 27.8, children: 0, smoker: 'no', region: 'southwest' },
  };

  document.querySelectorAll('.preset-chip').forEach((chip) => {
    chip.addEventListener('click', () => {
      const p = presets[chip.getAttribute('data-preset')];
      if (!p) return;

      ageInput.value = p.age;
      ageDisplay.textContent = `${p.age} yrs`;

      const sexRadio = document.querySelector(`input[name="sex"][value="${p.sex}"]`);
      if (sexRadio) sexRadio.checked = true;

      bmiInput.value = p.bmi;
      updateBmiBadge(p.bmi);

      childrenChips.forEach((c) => {
        if (c.getAttribute('data-val') === String(p.children)) {
          c.classList.add('active');
        } else {
          c.classList.remove('active');
        }
      });
      childrenInput.value = p.children;

      const smokerRadio = document.querySelector(`input[name="smoker"][value="${p.smoker}"]`);
      if (smokerRadio) smokerRadio.checked = true;

      const regionRadio = document.querySelector(`input[name="region"][value="${p.region}"]`);
      if (regionRadio) regionRadio.checked = true;

      runPrediction();
    });
  });

  // -------------------------------------------------------------
  // Animated Number Counter
  // -------------------------------------------------------------
  function animateValue(obj, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);
      const current = progress * (end - start) + start;
      obj.textContent = `₹${current.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
      if (progress < 1) {
        window.requestAnimationFrame(step);
      }
    };
    window.requestAnimationFrame(step);
  }

  // -------------------------------------------------------------
  // Prediction Execution
  // -------------------------------------------------------------
  async function runPrediction() {
    const age = parseInt(ageInput.value);
    const sex = document.querySelector('input[name="sex"]:checked')?.value || 'male';
    const bmi = parseFloat(bmiInput.value);
    const children = parseInt(childrenInput.value || 0);
    const smoker = document.querySelector('input[name="smoker"]:checked')?.value || 'no';
    const region = document.querySelector('input[name="region"]:checked')?.value || 'northwest';

    if (isNaN(bmi) || bmi < 10 || bmi > 70) {
      showToast('Please enter a valid BMI (10.0 - 70.0)');
      return;
    }

    btnSubmit.disabled = true;
    btnCaption.textContent = 'Calculating...';
    btnSpinner.style.display = 'inline-block';

    try {
      const response = await fetch('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ age, sex, bmi, children, smoker, region }),
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || 'Prediction calculation failed');
      }

      const annual = data.prediction.annual_charge;
      const monthly = data.prediction.monthly_charge;

      // Hero price animation
      animateValue(predictedAnnualEl, currentAnnualCost, annual, 500);
      predictedMonthlyEl.textContent = `₹${monthly.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
      currentAnnualCost = annual;

      // Risk badge styling matching palette
      const tier = data.risk_analysis.tier;
      riskTierEl.textContent = `${tier} Risk`;
      if (tier === 'Low') {
        riskTierEl.style.color = '#bce08a';
        riskTierEl.style.background = 'rgba(188, 224, 138, 0.12)';
        riskTierEl.style.borderColor = 'rgba(188, 224, 138, 0.35)';
      } else if (tier === 'Moderate') {
        riskTierEl.style.color = '#a4dad2';
        riskTierEl.style.background = 'rgba(164, 218, 210, 0.12)';
        riskTierEl.style.borderColor = 'rgba(164, 218, 210, 0.35)';
      } else {
        riskTierEl.style.color = '#f6d809';
        riskTierEl.style.background = 'rgba(246, 216, 9, 0.15)';
        riskTierEl.style.borderColor = 'rgba(246, 216, 9, 0.4)';
      }

      // Cost factors list
      factorListEl.innerHTML = '';
      data.risk_analysis.drivers.forEach((driver) => {
        const li = document.createElement('li');
        li.textContent = driver;
        factorListEl.appendChild(li);
      });

      // Meta row
      metaPatient.textContent = `${data.profile.age}y, ${data.profile.sex}`;
      metaBmiKids.textContent = `${data.profile.bmi} • ${data.profile.children} ${data.profile.children === 1 ? 'child' : 'children'}`;
      metaRegionSmoker.textContent = `${data.profile.region} • ${data.profile.smoker === 'Yes' ? 'Smoker' : 'Non-smoker'}`;

    } catch (err) {
      console.error(err);
      showToast(err.message || 'Error communicating with server');
    } finally {
      btnSubmit.disabled = false;
      btnCaption.textContent = 'Calculate Estimate';
      btnSpinner.style.display = 'none';
    }
  }

  // Form submit
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    runPrediction();
  });

  // Copy Calculation
  btnCopy.addEventListener('click', () => {
    const text = `CareCast AI Estimate:
Annual Premium: ${predictedAnnualEl.textContent} (${predictedMonthlyEl.textContent}/mo)
Profile: ${metaPatient.textContent} | BMI: ${metaBmiKids.textContent}
Region: ${metaRegionSmoker.textContent}`;

    navigator.clipboard.writeText(text)
      .then(() => showToast('Estimate copied to clipboard!'))
      .catch(() => showToast('Failed to copy.'));
  });

  // Toast
  let toastTimer = null;
  function showToast(msg) {
    toast.textContent = msg;
    toast.style.display = 'block';
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
      toast.style.display = 'none';
    }, 3000);
  }

  // Initial calculation on page load
  runPrediction();
});
