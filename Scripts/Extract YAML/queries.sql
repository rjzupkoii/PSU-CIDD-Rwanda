-- Get the YAML from the database
select c.id as configurationid, s.id as studyid, c.filename, s.name,  c.yaml
from sim.configuration c
  inner join sim.study s on s.id = c.studyid
where c.studyid = 29 or c.studyid = 30

-- Get the configurations and their replicates
select c.id as configurationid, s.id as studyid, c.filename, s.name, r.id as replicateid, r.starttime, r.endtime
from sim.configuration c
  inner join sim.study s on s.id = c.studyid
  inner join sim.replicate r on r.configurationid = c.id
where c.studyid = 29 or c.studyid = 30
order by s.id, c.id, r.id

-- Get the status quo reference data, normally run by Scripts/Incidence/allocations.py
SELECT one.id, one.location, 
    round(one.incidence, 2) AS incidence,
    round(CAST(one.pfpr2to10 AS numeric), 2) AS pfpr2to10,
    round(CAST(two.weightedoccurrences / one.infectedindividiuals AS numeric), 4) AS frequency,
    one.clinicalepisodes
FROM (
    SELECT r.id, msd.location,
    sum(msd.infectedindividuals) AS infectedindividiuals,
    sum(msd.clinicalepisodes) / (max(msd.population) / 1000.0) AS incidence,
    sum(msd.pfpr2to10 * msd.population) / sum(msd.population) AS pfpr2to10,
    sum(msd.clinicalepisodes) as clinicalepisodes
    FROM sim.replicate r
    INNER JOIN sim.monthlydata md ON md.replicateid = r.id
    INNER JOIN sim.monthlysitedata msd ON msd.monthlydataid = md.id
    WHERE r.configurationid = 11429
    AND md.dayselapsed between 7701 and 8036
    GROUP BY r.id, msd.location) one
INNER JOIN (
    SELECT r.id, mgd.location, sum(mgd.weightedoccurrences) as weightedoccurrences
    FROM sim.replicate r
    INNER JOIN sim.monthlydata md on md.replicateid = r.id
    INNER JOIN sim.monthlygenomedata mgd on mgd.monthlydataid = md.id
    INNER JOIN sim.genotype g ON g.id = mgd.genomeid
    WHERE r.configurationid = 11429
    AND md.dayselapsed BETWEEN 7701 and 8036
    AND g.name ~ '^.....H.'
    GROUP BY r.id, mgd.location) two ON one.id = two.id AND one.location = two.location