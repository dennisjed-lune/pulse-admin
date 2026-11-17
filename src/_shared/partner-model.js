/* Real partner data model (13 Nov 2026).
   Source: rfp-work/partner-data/*.json, pulled from the RFP sheets.
   Both prototypes run this same file, so Pulse Admin and LuneHub agree brand for brand and campaign for campaign.
   Supplier margin and raw network commission are not part of this model. */
const PM = (function (P) {
  const col = (d, name) => (d && d.columns ? d.columns.indexOf(name) : -1);
  const get = (d, row, name) => { const i = col(d, name); return i < 0 ? null : row[i]; };
  const PTS_PER_UNIT = 100;

  /* ---- YouGotaGift: one row for each brand, not one row for each denomination ---- */
  const ygg = P.yougotagift || { rows: [] };
  const nums = (s) => (String(s).match(/\d+(?:\.\d+)?/g) || []).map(Number);
  let n = 7001;
  const ITEMS = (ygg.rows || []).map((r) => {
    const den = get(ygg, r, 'denominations') || '';
    const v = nums(den);
    const lo = v.length ? Math.min.apply(null, v) : 0, hi = v.length ? Math.max.apply(null, v) : 0;
    return {
      id: 'ITM-' + n++, sup: 'ygg', sku: get(ygg, r, 'brandCode'), name: get(ygg, r, 'brand'),
      cat: get(ygg, r, 'category'), mkt: get(ygg, r, 'country'), cur: get(ygg, r, 'currency'),
      dtype: get(ygg, r, 'denominationType'), dtext: den, dmin: lo, dmax: hi,
      ptsMin: lo * PTS_PER_UNIT, ptsMax: hi * PTS_PER_UNIT,
      rtype: get(ygg, r, 'redemptionType'), validity: get(ygg, r, 'validity'),
      av: 'Not supplied', from: 'Not supplied', to: 'Not supplied'
    };
  });
  const MKTS = ITEMS.map((x) => x.mkt).filter((x, i, a) => a.indexOf(x) === i);
  const YGG_CATS = ITEMS.map((x) => x.cat).filter((x, i, a) => a.indexOf(x) === i);

  /* ---- Cosmo Points: connected, no catalogue for this bank yet ---- */
  const cp = P['cosmo-points'] || {};
  const COSMO = {
    partners: cp.partners || [],
    note: 'Each loyalty partner approves each bank. Approval takes 6 to 8 weeks.',
    types: (cp.partners || []).map((x) => x.type).filter((x, i, a) => a.indexOf(x) === i)
  };
  const COSMO_CATS = COSMO.types.map((t) => t + ' partners');

  const SUPL = [
    { id: 'ygg', name: 'YouGotaGift', conn: 'API', fulfils: 'Gift card brands', mkts: MKTS.join(', ') || 'Not supplied',
      avail: 'Not supplied', stage: 'Catalogue received', sync: 'Today 06:12', st: 'Live' },
    { id: 'cosmo', name: 'Cosmo Points', conn: 'API', fulfils: COSMO.types.join(' and ').toLowerCase() + ' loyalty partners',
      avail: 'Not supplied', stage: 'Partner approval in progress', sync: 'Not supplied', st: 'Catalogue pending' }
  ];

  /* Supplier and category rows a programme can activate. A row with no catalogue cannot go on. */
  const CATROWS = YGG_CATS.map((c) => ({ sup: 'ygg', cat: c }))
    .concat(COSMO_CATS.map((c) => ({ sup: 'cosmo', cat: c })));
  const CATS = YGG_CATS.concat(COSMO_CATS);

  /* ---- Affiliate networks ---- */
  const NETS = [
    ['Admitad', 'API', 'Today 06:00', 'Admitad API', 'Programmes, deeplinks, coupons and statistics', 'subid'],
    ['TakeAds', 'API', 'Today 05:45', 'Take API', 'Affiliate links, coupons, clicks and actions', 'subId']
  ];

  /* Lune sets the customer reward rate for each campaign. It is not the network commission.
     Keyed by the network programme or merchant ID, so both products show the same rate. */
  const REWARD = {
    '22897': [2, 'Nova Rewards', 1], '27912': [3, 'Nova Everyday Cashback', 1],
    '104523': [5, 'Nova Rewards', 0], '27630': [1, 'Nova Rewards', 1],
    '27913': [2.5, 'Nova Everyday Cashback', 1], '28855': [3, 'Nova Rewards', 0],
    '20021': [2, 'Nova Rewards', 1],
    '103555': [3, 'Nova Everyday Cashback', 1], '259450': [1, 'Nova Rewards', 0],
    '187822': [1, 'Nova Rewards', 1], '301639': [5, 'Nova Everyday Cashback', 0],
    '310570': [5, 'Nova Rewards', 1], '195455': [4, 'Nova Everyday Cashback', 0],
    '325297': [4, 'Nova Rewards', 1]
  };
  /* Brand shown for each Admitad programme. Each name is the brand inside the real programme name. */
  const ADM_BRAND = {
    '22897': 'Bloomingdales', '27912': 'Clarks Stores', '104523': 'DKNY', '27630': 'Huawei',
    '27913': 'Jashanmal', '28855': 'Kipling', '20021': 'Level Shoes'
  };
  const host = (u) => String(u || '').replace(/^https?:\/\//, '').replace(/^www\./, '').split('/')[0];

  const adm = P.admitad || { rows: [] };
  const tak = P.takeads || { rows: [] };
  let aid = 301;
  const AFF = [];
  (adm.rows || []).forEach((r) => {
    const nid = String(get(adm, r, 'admitadId')), rw = REWARD[nid] || [2, 'Nova Rewards', 0];
    const com = get(adm, r, 'commission');
    AFF.push({
      id: 'AL-' + aid++, net: 'Admitad', netId: nid,
      m: ADM_BRAND[nid] || get(adm, r, 'programme'), c: get(adm, r, 'programme'),
      cat: get(adm, r, 'category'), gcc: get(adm, r, 'gccCountries') || 'Not supplied',
      site: get(adm, r, 'website'), domain: host(get(adm, r, 'website')),
      type: get(adm, r, 'type') || 'Affiliate', hasCode: /promo code/i.test(get(adm, r, 'type') || ''),
      com: com || 'Not supplied', comKnown: !!com,
      rewardPct: rw[0], rw: rw[0] + '% cashback', prog: rw[1], on: !!rw[2],
      from: 'Not supplied', to: 'Not supplied', hold: 90
    });
  });
  (tak.rows || []).forEach((r) => {
    const nid = String(get(tak, r, 'takeadsMerchantId')), rw = REWARD[nid] || [2, 'Nova Rewards', 0];
    const com = get(tak, r, 'commission');
    AFF.push({
      id: 'AL-' + aid++, net: 'TakeAds', netId: nid,
      m: get(tak, r, 'merchant'), c: '',
      cat: get(tak, r, 'category'), gcc: get(tak, r, 'gccCountries') || 'Not supplied',
      site: '', domain: '',
      type: 'Affiliate', hasCode: false,
      com: com || 'Not supplied', comKnown: !!com,
      rewardPct: rw[0], rw: rw[0] + '% cashback', prog: rw[1], on: !!rw[2],
      from: 'Not supplied', to: 'Not supplied', hold: 90
    });
  });
  const AFF_CATS = AFF.map((a) => a.cat).filter((x, i, a) => a.indexOf(x) === i).sort();
  const affLabel = (a) => (a.c ? a.c : a.m);

  return { PTS_PER_UNIT: PTS_PER_UNIT, ITEMS: ITEMS, MKTS: MKTS, CATS: CATS, YGG_CATS: YGG_CATS,
    COSMO_CATS: COSMO_CATS, COSMO: COSMO, SUPL: SUPL, CATROWS: CATROWS,
    NETS: NETS, AFF: AFF, AFF_CATS: AFF_CATS, affLabel: affLabel,
    notes: { ygg: (P.yougotagift || {}).note || '', adm: (P.admitad || {}).note || '', tak: (P.takeads || {}).note || '' } };
})(/*PARTNER-DATA*/{});
