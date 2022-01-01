-- General aggergation query for 561H replicates
select sd.replicateid,
  filename,
  sd.dayselapsed, 
  infectedindividuals, 
  clinicalepisodes, 
  case when gd.clinicaloccurrences is null then 0 else gd.clinicaloccurrences end as clinicaloccurrences,
  case when gd.weightedoccurrences is null then 0 else gd.weightedoccurrences end as weightedoccurrences
from (
  select md.replicateid, md.dayselapsed, 
    sum(msd.infectedindividuals) as infectedindividuals, 
    sum(msd.clinicalepisodes) as clinicalepisodes
  from sim.monthlydata md
    inner join sim.monthlysitedata msd on msd.monthlydataid = md.id
  where md.replicateid in (select replicateid from v_561h_replicates)
    and md.dayselapsed > (11 * 365)
  group by md.replicateid, md.dayselapsed) sd
left join (
  select md.replicateid, md.dayselapsed, 
    sum(mgd.clinicaloccurrences) as clinicaloccurrences,
    sum(mgd.weightedoccurrences) as weightedoccurrences
  from sim.monthlydata md
    inner join sim.monthlygenomedata mgd on mgd.monthlydataid = md.id
    inner join sim.genotype g on g.id = mgd.genomeid
  where md.replicateid in (select replicateid from v_561h_replicates)
    and md.dayselapsed > (11 * 365)
    and g.name ~ '^.....H.'
  group by md.replicateid, md.dayselapsed) gd on (gd.replicateid = sd.replicateid and gd.dayselapsed = sd.dayselapsed)
inner join sim.replicate r on r.id = sd.replicateid
inner join sim.configuration c on c.id = r.configurationid
where r.endtime is not null
order by replicateid, dayselapsed

-- View to select 561H replicates and configurations from
CREATE VIEW v_561h_replicates AS
SELECT c.id AS configurationid, c.filename, r.id AS replicateid, c.studyid
FROM sim.configuration c
  INNER JOIN sim.replicate r ON r.configurationid = c.id
WHERE c.studyid > 2