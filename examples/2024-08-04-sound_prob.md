---
layout: post
title: "The Sound of Probability"
date: 2024-08-04
categories: [math, audio]
---

Have you ever wondered what probability distributions sound like?

Probably not. You probably have better things to do. 

But maybe you're curious now. I coded up some audio demos of probability distributions, and I found it kind of interesting.

You see, we're all used to **seeing** probability distributions. The bold and audacious curves of the the normal distribution. Or perhaps the timeless beauty of the exponential distribution.

If you've taken a stats class, these are old friends. Except you've never heard them. Let's change that.

## The Normal Distribution

The normal distribution, also known as the Gaussian distribution, is the most famous probability distribution. It's characterized by its bell-shaped curve and is defined by two parameters: the mean (μ) and the standard deviation (σ).

Let's listen to two normal distributions, both with a mean of 440 Hz (the A note), but with different standard deviations:

<div style="display: flex; justify-content: space-between;">
    <div style="width: 48%;">
        <p>σ = 20 Hz</p>
        <img src="/assets/images/normal_distribution_mean_440_std_20_num_samples_1000.png" alt="Normal Distribution (μ=440, σ=20)" style="width: 100%;">
        <audio controls style="width: 100%;">
            <source src="/assets/audio/normal_distribution_mean_440_std_20_num_samples_1000.wav" type="audio/wav">
            Your browser does not support the audio element.
        </audio>
    </div>
    <div style="width: 48%;">
        <p>σ = 100 Hz</p>
        <img src="/assets/images/normal_distribution_mean_440_std_100_num_samples_1000.png" alt="Normal Distribution (μ=440, σ=100)" style="width: 100%;">
        <audio controls style="width: 100%;">
            <source src="/assets/audio/normal_distribution_mean_440_std_100_num_samples_1000.wav" type="audio/wav">
            Your browser does not support the audio element.
        </audio>
    </div>
</div>

What do you hear? In both cases, the concentration of frequencies around 440 Hz gives us an a reasonable estimate of 440 as the mean (μ). However, the spread caused by the standard deviation adds a shimmering quality to the sound. 

Notice how the distribution with σ = 20 Hz sounds more focused, with a clearer pitch, our ears have a more precise estimate of the mean. The distribution with σ = 100 Hz, on the other hand, has a broader, more diffuse sound.

This auditory experience provides an intuitive understanding of how the standard deviation affects the spread of a normal distribution. A smaller standard deviation results in a more concentrated, "purer" sound, while a larger standard deviation creates a more complex, spread-out timbre.

## Poisson Distribution


# Convolving Distributions

As a final experiment, let's convolve two normal distributions. In probability theory, the convolution of two distributions represents the distribution of the sum of two independent random variables.

Here's what happens when we convolve a normal distribution (μ=440, σ=50) with another normal distribution (μ=550, σ=30):

![Convolved Distribution](/assets/images/convolved_distribution_loc_440_scale_50_loc_550_scale_30_num_samples_1000_operation_convolution.png)

<audio controls>
  <source src="/assets/audio/convolved_distribution_loc_440_scale_50_loc_550_scale_30_num_samples_1000_operation_convolution.wav" type="audio/wav">
  Your browser does not support the audio element.
</audio>

The resulting sound is a blend of the two original distributions, creating a rich and complex timbre.

What if we convolved two normal distributions with very similar means? Let's try it out with two distributions centered around 440 Hz and 445 Hz:

<div style="display: flex; justify-content: space-between;">
    <div style="width: 48%;">
        <p>Distribution 1: μ = 440 Hz, σ = 10 Hz</p>
        <img src="/assets/images/normal_distribution_mean_440_std_10_num_samples_1000.png" alt="Normal Distribution (μ=440, σ=10)" style="width: 100%;">
        <audio controls style="width: 100%;">
            <source src="/assets/audio/normal_distribution_mean_440_std_10_num_samples_1000.wav" type="audio/wav">
            Your browser does not support the audio element.
        </audio>
    </div>
    <div style="width: 48%;">
        <p>Distribution 2: μ = 445 Hz, σ = 10 Hz</p>
        <img src="/assets/images/normal_distribution_mean_445_std_10_num_samples_1000.png" alt="Normal Distribution (μ=445, σ=10)" style="width: 100%;">
        <audio controls style="width: 100%;">
            <source src="/assets/audio/normal_distribution_mean_445_std_10_num_samples_1000.wav" type="audio/wav">
            Your browser does not support the audio element.
        </audio>
    </div>
</div>

Now, let's listen to the convolution of these two distributions:

<div style="width: 100%;">
    <p>Convolved Distribution</p>
    <img src="/assets/images/convolved_distribution_mean1_440_std1_10_mean2_445_std2_10_num_samples_1000.png" alt="Convolved Distribution" style="width: 100%;">
    <audio controls style="width: 100%;">
        <source src="/assets/audio/convolved_distribution_mean1_440_std1_10_mean2_445_std2_10_num_samples_1000.wav" type="audio/wav">
        Your browser does not support the audio element.
    </audio>
</div>

What do you notice? The convolved distribution has a mean that's approximately the average of the two original means (around 442.5 Hz). However, the most interesting effect is in the sound itself. You might hear a subtle beating or wavering in the tone. This is because the two frequencies are very close together, causing interference patterns in the sound waves.

This phenomenon is what musicians call a "beat frequency." When two tones of slightly different frequencies are played together, you hear a pulsing or beating at a rate equal to the difference between the two frequencies. In our case, that's about 5 Hz (445 Hz - 440 Hz), which is in the audible range for most people. It occurs to me that this could be a way to perform signal processing of very high frequency signals that may be difficult to accurately measure. One could simply generate a few different frequencies and listen for the beat frequency, you could get a good approximation of the original signal. Somewhat related to the STFT.

This example demonstrates how convolution can reveal interesting properties that might not be immediately obvious from looking at the individual distributions. It also shows how mathematical concepts like convolution can have direct, perceivable effects in the physical world, such as in the behavior of sound waves.

## Conclusion

By translating probability distributions into sound, we can gain a new perspective on these mathematical concepts. The auditory experience provides an intuitive understanding of properties like spread, skewness, and central tendency.

It's a unique way to engage with these fundamental concepts.