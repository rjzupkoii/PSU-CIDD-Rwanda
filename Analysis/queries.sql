-- Basic monitoring query
select c.id as configurationid, c.studyid, filename, replicateid, 
  starttime, now() - starttime as runningtime, 
  max(dayselapsed) as modeldays
from sim.replicate r
  inner join sim.configuration c on c.id = r.configurationid
  inner join sim.monthlydata md on md.replicateid = r.id
where r.endtime is null
group by c.id, filename, replicateid, starttime
order by modeldays desc

-- Status of replicates for manuscript revisions
select configurationid, studyid, filename, 
  count(id) as total,
  sum(complete) as complete
from (
select c.id as configurationid, c.studyid, c.filename,
  r.id,
  case when r.endtime is null then 0 else 1 end as complete
from sim.configuration c
  inner join sim.replicate r on r.configurationid = c.id
where c.studyid in (19, 20, 21)
  and r.starttime > to_date('2023-01-01', 'YYYY-MM-DD')) iq
group by configurationid, studyid, filename
order by studyid, filename

-- All of the genotype frequencies for the given replicate
SELECT replicateid, dayselapsed, year, substring(g.name, 1, 7) as name, frequency
FROM (
	SELECT mgd.replicateid, mgd.genomeid, mgd.dayselapsed, 
		TO_CHAR(TO_DATE('2007-01-01', 'YYYY-MM-DD') + interval '1' day * mgd.dayselapsed, 'YYYY') AS year,
		mgd.weightedoccurrences / msd.infectedindividuals AS frequency
	FROM (
		SELECT md.replicateid, md.id, md.dayselapsed, mgd.genomeid, sum(mgd.weightedoccurrences) AS weightedoccurrences
		FROM sim.monthlydata md INNER JOIN sim.monthlygenomedata mgd ON mgd.monthlydataid = md.id
		WHERE md.replicateid = 51703 AND md.dayselapsed > 4015
		GROUP BY md.id, md.dayselapsed, mgd.genomeid) mgd
	INNER JOIN (
		SELECT md.id, sum(msd.infectedindividuals) AS infectedindividuals
		FROM sim.monthlydata md INNER JOIN sim.monthlysitedata msd ON msd.monthlydataid = md.id
		WHERE md.replicateid = 51703 AND md.dayselapsed > 4015
		GROUP BY md.id) msd 
	ON msd.id = mgd.id) frequency inner join sim.genotype g on g.id = frequency.genomeid


-- Status of all replicates
select configurationid, studyid, filename, 
  sum(complete) as complete,
  count(id) as total
from (
select c.id as configurationid, c.studyid, c.filename,
  r.id,
  case when r.endtime is null then 0 else 1 end as complete
from sim.configuration c
  inner join sim.replicate r on r.configurationid = c.id
where c.studyid not in (1, 2, 10)) iq
group by configurationid, studyid, filename
order by studyid, filename

-- General aggergation query for 561H replicates at the district level
select c.id as configurationid,
  sd.replicateid,
  sd.dayselapsed,
  sd.district,
  infectedindividuals, 
  clinicalepisodes, 
  case when gd.clinicaloccurrences is null then 0 else gd.clinicaloccurrences end as clinicaloccurrences,
  case when gd.weightedoccurrences is null then 0 else gd.weightedoccurrences end as weightedoccurrences
from (
  select md.replicateid, md.dayselapsed, msd.location as district,
    sum(msd.infectedindividuals) as infectedindividuals, 
    sum(msd.clinicalepisodes) as clinicalepisodes
  from sim.monthlydata md
    inner join sim.monthlysitedata msd on msd.monthlydataid = md.id
  where md.replicateid in (select replicateid from v_561h_replicates)
    and md.dayselapsed > (11 * 365)
  group by md.replicateid, md.dayselapsed, msd.location) sd
left join (
  select md.replicateid, md.dayselapsed, mgd.location as district,
    sum(mgd.clinicaloccurrences) as clinicaloccurrences,
    sum(mgd.weightedoccurrences) as weightedoccurrences
  from sim.monthlydata md
    inner join sim.monthlygenomedata mgd on mgd.monthlydataid = md.id
    inner join sim.genotype g on g.id = mgd.genomeid
  where md.replicateid in (select replicateid from v_561h_replicates)
    and md.dayselapsed > (11 * 365)
    and g.name ~ '^.....H.'
  group by md.replicateid, md.dayselapsed, mgd.location) gd 
  	on (gd.replicateid = sd.replicateid 
	  and gd.dayselapsed = sd.dayselapsed
	  and gd.district = sd.district)
inner join sim.replicate r on r.id = sd.replicateid
inner join sim.configuration c on c.id = r.configurationid
where r.endtime is not null
  and c.studyid = 4
order by replicateid, dayselapsed

-- General aggergation query for 561H validation replicates at the district level
SELECT c.id as configurationid, sd.replicateid, sd.dayselapsed,
  sd.district, infectedindividuals,  clinicalepisodes, 
  CASE WHEN gd.occurrences IS NULL THEN 0 else gd.occurrences END AS occurrences,
  CASE WHEN gd.clinicaloccurrences IS NULL THEN 0 else gd.clinicaloccurrences END AS clinicaloccurrences,
  CASE WHEN gd.weightedoccurrences IS NULL THEN 0 else gd.weightedoccurrences END AS weightedoccurrences,
  treatments,
  treatmentfailures,
  genotypecarriers
FROM (
  SELECT md.replicateid, md.dayselapsed, msd.location AS district,
    sum(msd.infectedindividuals) AS infectedindividuals, 
    sum(msd.clinicalepisodes) AS clinicalepisodes,
    sum(msd.treatments) AS treatments,
    sum(msd.treatmentfailures) as treatmentfailures,
    sum(genotypecarriers) as genotypecarriers
  FROM sim.monthlydata md
    INNER JOIN sim.monthlysitedata msd on msd.monthlydataid = md.id
  WHERE md.replicateid IN (SELECT replicateid FROM v_561h_replicates)
    AND md.dayselapsed > 365
  GROUP BY md.replicateid, md.dayselapsed, msd.location) sd
LEFT JOIN (
  SELECT md.replicateid, md.dayselapsed, mgd.location AS district,
  sum(mgd.occurrences) AS occurrences,
    sum(mgd.clinicaloccurrences) AS clinicaloccurrences,
    sum(mgd.weightedoccurrences) AS weightedoccurrences
  FROM sim.monthlydata md
    INNER JOIN sim.monthlygenomedata mgd on mgd.monthlydataid = md.id
    INNER JOIN sim.genotype g on g.id = mgd.genomeid
  WHERE md.replicateid IN (SELECT replicateid FROM v_561h_replicates)
    AND md.dayselapsed > 365
    AND g.name ~ '^.....H.'
  GROUP BY md.replicateid, md.dayselapsed, mgd.location) gd ON (gd.replicateid = sd.replicateid 
    AND gd.dayselapsed = sd.dayselapsed
    AND gd.district = sd.district)
  INNER JOIN sim.replicate r on r.id = sd.replicateid
  INNER JOIN sim.configuration c on c.id = r.configurationid
WHERE r.endtime is not null
  AND c.id = 7462
ORDER BY replicateid, dayselapsed

-- View to select 561H replicates and configurations from
CREATE VIEW v_561h_replicates AS
SELECT c.id AS configurationid, c.filename, r.id AS replicateid, c.studyid
FROM sim.configuration c
  INNER JOIN sim.replicate r ON r.configurationid = c.id
WHERE c.id = 7462

-- Query to determine what time frame manuscript replicates were from
  SELECT configurationid, s.name, filename, min(starttime), max(endtime)
  FROM (
  SELECT c.id AS configurationid, 
    c.studyid, 
    c.filename, 
    r.starttime,
    r.endtime
  FROM sim.replicate r
    INNER JOIN sim.configuration c ON c.id = r.configurationid
  WHERE r.endtime IS NOT null AND c.id in (
    SELECT max(c.id)
    FROM sim.configuration c
    WHERE c.filename in (
      SELECT distinct c.filename
      FROM sim.configuration c
      WHERE c.studyid NOT IN (1, 2, 3, 10))
    GROUP BY c.filename, c.studyid)) iq
 INNER JOIN sim.study s ON s.id = studyid
 GROUP BY configurationid, studyid, filename, s.name
 ORDER BY studyid, filename

-- Query to check the status of the final replicates for the manuscript
 SELECT configurationid, studyid, filename, 
  sum(complete) AS complete,
  count(id) AS total, min(starttime), max(starttime)
FROM (
	SELECT c.id AS configurationid, c.studyid, c.filename,
	  r.id, r.starttime,
	  CASE WHEN r.endtime IS NULL THEN 0 ELSE 1 END AS complete
	FROM sim.configuration c
	  INNER JOIN sim.replicate r ON r.configurationid = c.id
	where c.id in (
		SELECT max(c.id) AS configurationid
		FROM sim.configuration c
		WHERE c.studyid NOT IN (1, 2, 3, 10)
		GROUP BY c.studyid, c.filename)
	  AND r.starttime > '2022-06-30') iq
GROUP BY configurationid, studyid, filename
ORDER BY studyid, filename

-- Validation study query, constrained to model year 2020
-- Date span for model year 2022: AND md.dayselapsed between 6939 and 7274
SELECT c.id as configurationid, sd.replicateid, sd.district, 
max(population) / 0.25 as population, 
sum(clinicalepisodes) / 0.25 as clinicalepisodes,
sum(treatments) / 0.25 as treatments,
sum(treatmentfailures) / 0.25 as treatmentfailures,
round(sum(clinicalepisodes) / (max(population) / 1000), 2) annualclinical_per1000,
round(sum(treatments) / (max(population) / 1000), 2) annualtreated_per1000
FROM (
SELECT md.replicateid, md.dayselapsed, msd.location AS district,
  sum(msd.population) as population,
  sum(msd.clinicalepisodes) AS clinicalepisodes,
  sum(msd.infectedindividuals) as infectedindividuals,
  sum(msd.treatments) AS treatments,
  sum(msd.treatmentfailures) as treatmentfailures
FROM sim.monthlydata md
  INNER JOIN sim.monthlysitedata msd on msd.monthlydataid = md.id
WHERE md.replicateid = 53336
  AND md.dayselapsed between 6209 and 6544
GROUP BY md.replicateid, md.dayselapsed, msd.location) sd
INNER JOIN sim.replicate r on r.id = sd.replicateid
INNER JOIN sim.configuration c on c.id = r.configurationid
WHERE r.endtime is not null
AND r.id = 53336
GROUP BY c.id, sd.replicateid, sd.district
ORDER BY district
