---
layout: portfolio
permalink: /aboutme/
title: About
hide_kicker: true
description: Amir Mohammadi's education, research experience, mentoring, teaching, academic service, and awards.
---
<div class="prose">
  <p>I’m Amir, a Computer Engineering PhD candidate at Texas A&M University. I develop and evaluate AI models for problems in health, imaging, and acoustics.</p>
  <p>My doctoral work includes adapting vision-language foundation models for histopathology, developing parameter-efficient fine-tuning methods, and modeling physiological time series with physics-informed neural networks. I am also contributing to computer vision evaluation pipelines spanning classification, segmentation, and object detection.</p>
  <p>Before my PhD, I designed an integrated wearable stress-detection system during my master’s at Sharif University of Technology, developing both its electronics and machine-learning algorithms.</p>
</div>
<section class="section" aria-labelledby="education-title"><h2 id="education-title">Education</h2><div class="timeline">{% for item in site.data.cv.education %}<article class="timeline-item"><p class="timeline-date">{{ item.dates }}</p><div><h3>{{ item.degree }}</h3><p class="institution">{{ item.institution }}</p><p class="small-note">{{ item.location }}</p><p class="thesis">{% if forloop.last %}Project{% else %}Thesis{% endif %}: {{ item.thesis }}</p></div></article>{% endfor %}</div></section>
<section class="section" aria-labelledby="experience-title"><h2 id="experience-title">Research experience</h2><div class="timeline">{% for item in site.data.cv.experience %}<article class="timeline-item"><p class="timeline-date">{{ item.dates }}</p><div><h3>{{ item.role }}</h3><p class="institution">{{ item.institution }}</p><ul class="body-list">{% for bullet in item.about_bullets %}<li>{{ bullet }}</li>{% endfor %}</ul></div></article>{% endfor %}</div></section>
<section class="section two-column" aria-label="Teaching and academic service"><div><h2>Teaching & mentoring</h2><ul class="body-list">{% for item in site.data.cv.mentoring %}<li>{{ item }}</li>{% endfor %}</ul></div><div><h2>Academic service</h2><ul class="body-list">{% for item in site.data.cv.service %}<li>{{ item }}</li>{% endfor %}</ul></div></section>
<section class="section two-column" aria-label="Skills and awards"><div><h2>Tools & skills</h2><dl class="skills">{% for skill in site.data.cv.skills %}<dt>{{ skill.label }}</dt><dd>{{ skill.items }}</dd>{% endfor %}</dl></div><div><h2>Recognition</h2><p>{{ site.data.cv.support }}</p><ul class="body-list">{% for award in site.data.cv.awards %}<li>{{ award.title }} <span class="small-note">({{ award.date }})</span></li>{% endfor %}</ul><h3>Languages</h3><p>{{ site.data.cv.languages }}</p></div></section>
