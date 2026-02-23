import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO
from datetime import date
import os

st.set_page_config(page_title="Simulador de Cría - Don Tito", page_icon="🐄", layout="wide")
LOGO_PATH = os.path.join(os.path.dirname(__file__), "logo.jpg")

def fm(n, d=0):
    if d==0: s=f"{abs(n):,.0f}"
    elif d==1: s=f"{abs(n):,.1f}"
    elif d==2: s=f"{abs(n):,.2f}"
    else: s=f"{abs(n):,.{d}f}"
    s=s.replace(",","X").replace(".",",").replace("X",".")
    return ("-"+s) if n<0 else s
def fmd(n,d=0): return "$"+fm(n,d)
def fmp(n): return fm(n*100,1)+"%"

st.markdown("""
<style>
    .main .block-container{padding-top:1rem;max-width:1200px}
    .kpi-card{background:linear-gradient(135deg,#1a5276 0%,#2e86c1 100%);border-radius:12px;padding:18px 20px;text-align:center;color:white;box-shadow:0 4px 6px rgba(0,0,0,0.1)}
    .kpi-card h3{margin:0;font-size:.85rem;opacity:.9;font-weight:400}
    .kpi-card h1{margin:4px 0 0 0;font-size:1.8rem;font-weight:700}
    .kpi-negative{background:linear-gradient(135deg,#922b21 0%,#e74c3c 100%)}
    .kpi-green{background:linear-gradient(135deg,#1e6e3e 0%,#27ae60 100%)}
    .alert-red{background-color:#f8d7da;border:2px solid #c00000;border-radius:10px;padding:12px 20px;color:#721c24;font-weight:bold;text-align:center;font-size:1.1rem;margin:10px 0}
    .alert-green{background-color:#d4edda;border:2px solid #28a745;border-radius:10px;padding:12px 20px;color:#155724;font-weight:bold;text-align:center;font-size:1.1rem;margin:10px 0}
</style>
""",unsafe_allow_html=True)

def default(k,v):
    if k not in st.session_state: st.session_state[k]=v

RES=['Pastura megatérmica','Pastura templada','Verdeo invierno','Verdeo verano','Campo natural','Monte/Silvopastoril']
for r in RES:
    default(f"sup_{r}",0.0);default(f"rec_{r}",0.0);default(f"mes_{r}",0.0);default(f"impl_{r}",0.0);default(f"mant_{r}",0.0)
default("vu_prad",5.0)
for k,v in [("n_vacas",0.0),("ev_vaca",1.0),("n_vaq",0.0),("ev_vaq",0.8),("n_toros",0.0),("ev_toro",1.3),("prenez",85),("paricion",95),("perdidas",5),("peso_dest",170.0),("vu_vacas",6.0),("mort_vacas",1.0),("vu_toros",4.0),("mort_toros",1.0)]:
    default(k,v)
for k,v in [("p_tern",0.0),("p_vaca",0.0),("p_toro_ref",0.0),("kg_vaca_ref",400.0),("kg_toro_ref",700.0),("n_vaq_exc",0.0),("kg_vaq_exc",300.0),("p_vaq_exc",0.0),("p_toro_compra",0.0),("kg_toro_compra",700.0),("gc_venta",6.0),("gc_compra",6.0)]:
    default(k,v)
for k,v in [("si_cant",0.0),("si_precio",0.0),("se_cant",0.0),("se_precio",0.0),("heno_cant",0.0),("heno_precio",0.0),("sal_cant",0.0),("sal_precio",0.0),("san_vientre",0.0),("san_toro",0.0),("n_enc",0.0),("s_enc",0.0),("n_peon",0.0),("s_peon",0.0),("c_comb",0.0),("c_alamb",0.0),("c_varios",0.0)]:
    default(k,v)
default("es_arrendado",False);default("arriendo_kg",0.0);default("arriendo_precio",0.0)

col_logo,col_title=st.columns([1,5])
with col_logo:
    if os.path.exists(LOGO_PATH): st.image(LOGO_PATH,width=120)
with col_title:
    st.markdown("# SIMULADOR DE CRÍA")
    st.markdown("*Modelo de simulación para cálculo de margen bruto.*")
st.divider()

tab1,tab2,tab3,tab4,tab5,tab6=st.tabs(["🌿 Forrajero","🐂 Rodeo","💵 Ingresos","📋 Costos","📈 Resultados","🔄 Sensibilidad"])

with tab1:
    st.subheader("🌿 Planteo Forrajero")
    hc=st.columns([3,2,2,1.5,2,2])
    hc[0].markdown("**Recurso**");hc[1].markdown("**Sup (ha)**");hc[2].markdown("**EV/ha/año**");hc[3].markdown("**Meses**");hc[4].markdown("**Impl ($/ha)**");hc[5].markdown("**Mant ($/ha/año)**")
    for r in RES:
        c=st.columns([3,2,2,1.5,2,2])
        c[0].markdown(f"*{r}*")
        c[1].number_input("ha",0.0,50000.0,step=1.0,format="%.1f",key=f"sup_{r}",label_visibility="collapsed")
        c[2].number_input("EV",0.0,5.0,step=0.1,format="%.1f",key=f"rec_{r}",label_visibility="collapsed")
        c[3].number_input("m",0.0,12.0,step=1.0,format="%.0f",key=f"mes_{r}",label_visibility="collapsed")
        c[4].number_input("i",0.0,5000000.0,step=1000.0,format="%.0f",key=f"impl_{r}",label_visibility="collapsed")
        c[5].number_input("mt",0.0,5000000.0,step=500.0,format="%.0f",key=f"mant_{r}",label_visibility="collapsed")
    st.markdown("---")
    st.number_input("Vida útil praderas (años)",1.0,30.0,step=1.0,format="%.0f",key="vu_prad")

recursos={r:{'sup':st.session_state[f"sup_{r}"],'recep':st.session_state[f"rec_{r}"],'meses':st.session_state[f"mes_{r}"],'costo_impl':st.session_state[f"impl_{r}"],'costo_mant':st.session_state[f"mant_{r}"]} for r in RES}
vida_util_pradera=st.session_state["vu_prad"]
sup_total=sum(r['sup'] for r in recursos.values())
sup_efectiva=sum(r['sup']*r['meses']/12 for r in recursos.values() if r['meses']>0)
ev_capacidad=sum(r['sup']*r['recep']*r['meses']/12 for r in recursos.values() if r['meses']>0)
costo_impl_total=sum(r['sup']*r['costo_impl'] for r in recursos.values())
costo_mant_total=sum(r['sup']*r['costo_mant'] for r in recursos.values())
amort_praderas=costo_impl_total/vida_util_pradera if vida_util_pradera>0 else 0
costo_forrajero_total=amort_praderas+costo_mant_total

with tab1:
    st.markdown("### Resumen")
    r1,r2,r3,r4=st.columns(4)
    r1.metric("Sup Total",f"{fm(sup_total)} ha");r2.metric("Sup Efectiva",f"{fm(sup_efectiva,1)} ha")
    r3.metric("Capacidad",f"{fm(ev_capacidad,1)} EV");r4.metric("Costo Forraj./año",fmd(costo_forrajero_total))
    df=[{'Recurso':n,'Sup (ha)':r['sup']} for n,r in recursos.items() if r['sup']>0]
    if len(df)>1:
        fig=px.pie(pd.DataFrame(df),values='Sup (ha)',names='Recurso',title='Distribución',color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(height=350);st.plotly_chart(fig,use_container_width=True)

with tab2:
    st.subheader("🐂 Rodeo y Reproducción")
    c1,c2=st.columns(2)
    with c1:
        st.markdown("**Composición**")
        rc=st.columns(3)
        rc[0].number_input("Vacas (cab)",0.0,10000.0,step=10.0,format="%.0f",key="n_vacas")
        rc[1].number_input("Vaquillonas 1er serv.",0.0,5000.0,step=5.0,format="%.0f",key="n_vaq")
        rc[2].number_input("Toros (cab)",0.0,500.0,step=1.0,format="%.0f",key="n_toros")
        rc2=st.columns(3)
        rc2[0].number_input("EV vaca",0.5,2.0,step=0.05,format="%.2f",key="ev_vaca")
        rc2[1].number_input("EV vaq.",0.5,2.0,step=0.05,format="%.2f",key="ev_vaq")
        rc2[2].number_input("EV toro",0.5,2.0,step=0.05,format="%.2f",key="ev_toro")
    with c2:
        st.markdown("**Reproductivos**")
        st.slider("% Preñez",0,100,key="prenez");st.slider("% Parición",0,100,key="paricion")
        st.slider("% Pérdidas parto-destete",0,30,key="perdidas")
        st.number_input("Peso destete (kg/cab)",50.0,300.0,step=1.0,format="%.1f",key="peso_dest")
    st.markdown("**Vida útil y Mortandad**")
    vc=st.columns(4)
    vc[0].number_input("VU vacas (años)",1.0,15.0,step=1.0,format="%.0f",key="vu_vacas")
    vc[1].number_input("% Mort. vacas",0.0,10.0,step=0.5,format="%.1f",key="mort_vacas")
    vc[2].number_input("VU toros (años)",1.0,10.0,step=1.0,format="%.0f",key="vu_toros")
    vc[3].number_input("% Mort. toros",0.0,10.0,step=0.5,format="%.1f",key="mort_toros")

n_vacas=st.session_state["n_vacas"];n_vaq=st.session_state["n_vaq"];n_toros=st.session_state["n_toros"]
ev_vaca=st.session_state["ev_vaca"];ev_vaq=st.session_state["ev_vaq"];ev_toro=st.session_state["ev_toro"]
pct_prenez=st.session_state["prenez"]/100;pct_paricion=st.session_state["paricion"]/100;pct_perdidas=st.session_state["perdidas"]/100
peso_destete=st.session_state["peso_dest"];vu_vacas=st.session_state["vu_vacas"];mort_vacas=st.session_state["mort_vacas"]/100
vu_toros=st.session_state["vu_toros"];mort_toros=st.session_state["mort_toros"]/100
vientres=n_vacas+n_vaq;ev_rodeo=n_vacas*ev_vaca+n_vaq*ev_vaq+n_toros*ev_toro
balance_ev=ev_capacidad-ev_rodeo;pct_ocupacion=ev_rodeo/ev_capacidad if ev_capacidad>0 else 0
vacas_prenadas=round(vientres*pct_prenez);terneros_nacidos=round(vacas_prenadas*pct_paricion)
terneros_destetados=round(terneros_nacidos*(1-pct_perdidas));pct_destete_efect=terneros_destetados/vientres if vientres>0 else 0
reposicion_hembras=round(n_vacas/vu_vacas+n_vacas*mort_vacas) if vu_vacas>0 else 0
reposicion_toros=round(n_toros/vu_toros+n_toros*mort_toros) if vu_toros>0 else 0
terneros_venta=max(0,terneros_destetados-reposicion_hembras)
vacas_refugo=round(n_vacas/vu_vacas) if vu_vacas>0 else 0;toros_refugo=round(n_toros/vu_toros) if vu_toros>0 else 0

with tab2:
    st.markdown("---")
    if sup_total>0 and vientres>0:
        if balance_ev<0:st.markdown(f'<div class="alert-red">⚠️ EXCEDE RECEPTIVIDAD — Rodeo: {fm(ev_rodeo,1)} EV / Capacidad: {fm(ev_capacidad,1)} EV ({fmp(pct_ocupacion)})</div>',unsafe_allow_html=True)
        else:st.markdown(f'<div class="alert-green">✅ Balance OK — Rodeo: {fm(ev_rodeo,1)} EV / Capacidad: {fm(ev_capacidad,1)} EV ({fmp(pct_ocupacion)})</div>',unsafe_allow_html=True)
    st.markdown("### Cadena Reproductiva")
    co1,co2=st.columns(2)
    with co1:
        st.dataframe(pd.DataFrame({'Cat.':['Vacas','Vaq.','Toros'],'Cab':[fm(n_vacas),fm(n_vaq),fm(n_toros)],'EV':[ev_vaca,ev_vaq,ev_toro],'EV Tot':[fm(n_vacas*ev_vaca,1),fm(n_vaq*ev_vaq,1),fm(n_toros*ev_toro,1)]}),use_container_width=True,hide_index=True)
        st.metric("Total Vientres",fm(vientres));st.metric("EV Rodeo",fm(ev_rodeo,1))
    with co2:
        st.dataframe(pd.DataFrame({'Etapa':['Entorados','Preñadas','Nacidos','Destetados','Retenidas','Para venta'],'Cab':[fm(vientres),fm(vacas_prenadas),fm(terneros_nacidos),fm(terneros_destetados),fm(reposicion_hembras),fm(terneros_venta)]}),use_container_width=True,hide_index=True)
        st.metric("% Destete Efect.",fmp(pct_destete_efect))
    if vientres>0:
        ff=go.Figure(go.Funnel(y=['Entorados','Preñadas','Nacidos','Destetados','Venta'],x=[vientres,vacas_prenadas,terneros_nacidos,terneros_destetados,terneros_venta],textinfo="value+percent initial",marker=dict(color=['#2e86c1','#2874a6','#1a5276','#148f77','#27ae60'])))
        ff.update_layout(title="Embudo Reproductivo",height=400);st.plotly_chart(ff,use_container_width=True)

with tab3:
    st.subheader("💵 Ingresos y Precios")
    c1,c2=st.columns(2)
    with c1:
        st.markdown("**Precios Venta**")
        st.number_input("Precio ternero ($/kg)",0.0,1e7,step=50.0,format="%.2f",key="p_tern")
        st.number_input("Precio vaca ref. ($/kg)",0.0,1e7,step=50.0,format="%.2f",key="p_vaca")
        st.number_input("Precio toro ref. ($/kg)",0.0,1e7,step=50.0,format="%.2f",key="p_toro_ref")
        st.number_input("Precio vaq. exc. ($/kg)",0.0,1e7,step=50.0,format="%.2f",key="p_vaq_exc")
    with c2:
        st.markdown("**Pesos y Cantidades**")
        st.number_input("Peso vaca ref. (kg)",0.0,800.0,step=10.0,format="%.1f",key="kg_vaca_ref")
        st.number_input("Peso toro ref. (kg)",0.0,1200.0,step=10.0,format="%.1f",key="kg_toro_ref")
        st.number_input("Vaq. excedentes (cab)",0.0,1000.0,step=1.0,format="%.0f",key="n_vaq_exc")
        st.number_input("Peso vaq. exc. (kg)",0.0,500.0,step=10.0,format="%.1f",key="kg_vaq_exc")
    st.markdown("**Repos. Toros (compra)**")
    tc=st.columns(2)
    tc[0].number_input("Precio toro repos. ($/cab)",0.0,5e7,step=50000.0,format="%.0f",key="p_toro_compra")
    tc[1].number_input("Peso toro compra (kg)",0.0,1200.0,step=10.0,format="%.1f",key="kg_toro_compra")
    st.markdown("**Gtos. Comercialización**")
    gc=st.columns(2)
    gc[0].number_input("% Gtos. ventas",0.0,20.0,step=0.5,format="%.1f",key="gc_venta")
    gc[1].number_input("% Gtos. compras",0.0,20.0,step=0.5,format="%.1f",key="gc_compra")

precio_ternero=st.session_state["p_tern"];precio_vaca_ref=st.session_state["p_vaca"];precio_toro_ref=st.session_state["p_toro_ref"]
precio_vaq_exc=st.session_state["p_vaq_exc"];peso_vaca_ref=st.session_state["kg_vaca_ref"];peso_toro_ref=st.session_state["kg_toro_ref"]
n_vaq_exc=st.session_state["n_vaq_exc"];peso_vaq_exc=st.session_state["kg_vaq_exc"]
precio_toro_compra=st.session_state["p_toro_compra"];peso_toro_compra=st.session_state["kg_toro_compra"]
gtos_com_venta=st.session_state["gc_venta"]/100;gtos_com_compra=st.session_state["gc_compra"]/100
ing_tern=terneros_venta*peso_destete*precio_ternero;ing_vac=vacas_refugo*peso_vaca_ref*precio_vaca_ref
ing_tor=toros_refugo*peso_toro_ref*precio_toro_ref;ing_vaq=n_vaq_exc*peso_vaq_exc*precio_vaq_exc
ing_bruto=ing_tern+ing_vac+ing_tor+ing_vaq;gtos_ventas=ing_bruto*gtos_com_venta;ing_neto_v=ing_bruto-gtos_ventas
costo_toros=reposicion_toros*precio_toro_compra;gtos_compras=costo_toros*gtos_com_compra
costo_repos=costo_toros+gtos_compras;ing_neto_total=ing_neto_v-costo_repos
kg_vend=terneros_venta*peso_destete+vacas_refugo*peso_vaca_ref+toros_refugo*peso_toro_ref+n_vaq_exc*peso_vaq_exc
kg_comp=reposicion_toros*peso_toro_compra;kg_prod=kg_vend-kg_comp

with tab3:
    st.markdown("---");st.markdown("### Detalle Ventas")
    vd=[]
    for cat,cab,kg,pr,ib in [('Terneros',terneros_venta,peso_destete,precio_ternero,ing_tern),('Vacas ref.',vacas_refugo,peso_vaca_ref,precio_vaca_ref,ing_vac),('Toros ref.',toros_refugo,peso_toro_ref,precio_toro_ref,ing_tor),('Vaq. exc.',n_vaq_exc,peso_vaq_exc,precio_vaq_exc,ing_vaq)]:
        if cab>0 and pr>0:vd.append({'Cat.':cat,'Cab':fm(cab),'Kg/cab':fm(kg,1),'Kg tot':fm(cab*kg),'$/kg':fmd(pr,2),'Ing.$':fmd(ib)})
    if vd:st.dataframe(pd.DataFrame(vd),use_container_width=True,hide_index=True)
    m1,m2,m3=st.columns(3)
    m1.metric("Ing. Bruto",fmd(ing_bruto));m2.metric("Gtos. Com.",f"-{fmd(gtos_ventas)}");m3.metric("Ing. Neto Total",fmd(ing_neto_total))

with tab4:
    st.subheader("📋 Costos Directos")
    c1,c2=st.columns(2)
    with c1:
        st.markdown("**Suplementación**")
        sc=st.columns(2);sc[0].number_input("Sup.inv.(kg/vac/año)",0.0,1000.0,step=10.0,format="%.1f",key="si_cant");sc[1].number_input("$/kg inv.",0.0,1e7,step=10.0,format="%.2f",key="si_precio")
        sc2=st.columns(2);sc2[0].number_input("Sup.est.(kg/vac/año)",0.0,1000.0,step=10.0,format="%.1f",key="se_cant");sc2[1].number_input("$/kg est.",0.0,1e7,step=10.0,format="%.2f",key="se_precio")
        sc3=st.columns(2);sc3[0].number_input("Heno (unid/vac/año)",0.0,50.0,step=0.5,format="%.1f",key="heno_cant");sc3[1].number_input("$/rollo",0.0,1e7,step=1000.0,format="%.0f",key="heno_precio")
        sc4=st.columns(2);sc4[0].number_input("Sal (kg/vac/año)",0.0,100.0,step=1.0,format="%.1f",key="sal_cant");sc4[1].number_input("$/kg sal",0.0,1e7,step=50.0,format="%.2f",key="sal_precio")
    with c2:
        st.markdown("**Sanidad**");st.number_input("Sanidad $/vientre/año",0.0,1e7,step=500.0,format="%.0f",key="san_vientre");st.number_input("Sanidad $/toro/año",0.0,1e7,step=500.0,format="%.0f",key="san_toro")
        st.markdown("**Personal**")
        pc=st.columns(2);pc[0].number_input("Encargados",0.0,10.0,step=1.0,format="%.0f",key="n_enc");pc[1].number_input("Sueldo enc. $/mes",0.0,5e7,step=10000.0,format="%.0f",key="s_enc")
        pc2=st.columns(2);pc2[0].number_input("Peones",0.0,20.0,step=1.0,format="%.0f",key="n_peon");pc2[1].number_input("Sueldo peón $/mes",0.0,5e7,step=10000.0,format="%.0f",key="s_peon")
    st.markdown("**Otros**")
    oc=st.columns(3);oc[0].number_input("Combustible $/año",0.0,1e9,step=10000.0,format="%.0f",key="c_comb");oc[1].number_input("Alambrados $/año",0.0,1e9,step=10000.0,format="%.0f",key="c_alamb");oc[2].number_input("Varios $/año",0.0,1e9,step=5000.0,format="%.0f",key="c_varios")
    st.markdown("---")
    st.markdown("**🏠 Arriendo**")
    es_arr=st.checkbox("Campo arrendado",key="es_arrendado")
    if es_arr:
        ac=st.columns(2)
        ac[0].number_input("Arriendo (kg/ha/año)",0.0,500.0,step=1.0,format="%.1f",key="arriendo_kg")
        ac[1].number_input("Precio kg arriendo ($/kg)",0.0,1e7,step=50.0,format="%.2f",key="arriendo_precio")

c_alim=(st.session_state["si_cant"]*st.session_state["si_precio"]+st.session_state["se_cant"]*st.session_state["se_precio"]+st.session_state["heno_cant"]*st.session_state["heno_precio"]+st.session_state["sal_cant"]*st.session_state["sal_precio"])*vientres
c_san=st.session_state["san_vientre"]*vientres+st.session_state["san_toro"]*n_toros
c_pers=(st.session_state["n_enc"]*st.session_state["s_enc"]+st.session_state["n_peon"]*st.session_state["s_peon"])*13
c_otros=st.session_state["c_comb"]+st.session_state["c_alamb"]+st.session_state["c_varios"]
c_arriendo=0
if st.session_state["es_arrendado"]:
    c_arriendo=st.session_state["arriendo_kg"]*st.session_state["arriendo_precio"]*sup_total
cd_sin_rep=c_alim+c_san+c_pers+c_otros+costo_forrajero_total+c_arriendo
cd_total=cd_sin_rep+costo_repos
mb=ing_neto_total-cd_sin_rep

with tab4:
    st.markdown("### Resumen Costos")
    ci={'Alimentación':c_alim,'Sanidad':c_san,'Personal':c_pers,'Otros':c_otros,'Forrajero':costo_forrajero_total,'Repos. toros':costo_repos}
    if c_arriendo>0: ci['Arriendo']=c_arriendo
    cdf=[{'Ítem':k,'$/año':fmd(v),'$/ha':fmd(v/sup_total,1) if sup_total>0 else "$0",'$/vaca':fmd(v/vientres,1) if vientres>0 else "$0",'%':fmp(v/cd_total) if cd_total>0 else "0%"} for k,v in ci.items()]
    st.dataframe(pd.DataFrame(cdf),use_container_width=True,hide_index=True)
    mc=st.columns(3);mc[0].metric("Total CD",fmd(cd_total));mc[1].metric("$/ha",fmd(cd_total/sup_total) if sup_total>0 else "$0");mc[2].metric("$/vaca",fmd(cd_total/vientres) if vientres>0 else "$0")
    if c_arriendo>0:
        st.info(f"Arriendo: {fm(st.session_state['arriendo_kg'],1)} kg/ha/año × {fmd(st.session_state['arriendo_precio'],2)}/kg × {fm(sup_total)} ha = {fmd(c_arriendo)}/año")
    dp=[{'Ítem':k,'val':v} for k,v in ci.items() if v>0]
    if dp:
        fc=px.pie(pd.DataFrame(dp),values='val',names='Ítem',title='Composición Costos',color_discrete_sequence=px.colors.qualitative.Set1)
        fc.update_layout(height=400);st.plotly_chart(fc,use_container_width=True)

mb_ha=mb/sup_total if sup_total>0 else 0;mb_vaca=mb/vientres if vientres>0 else 0
kg_ha=kg_prod/sup_total if sup_total>0 else 0;kg_vaca=kg_prod/vientres if vientres>0 else 0
carga=vientres/sup_total if sup_total>0 else 0;c_unit=cd_total/kg_prod if kg_prod>0 else 0
p_neto=ing_neto_v/kg_vend if kg_vend>0 else 0;mb_cd=mb/cd_total if cd_total>0 else 0
pto_eq=cd_total/(precio_ternero*peso_destete) if precio_ternero*peso_destete>0 else 0

def kpi(l,v,c="kpi-card"):return f'<div class="{c}"><h3>{l}</h3><h1>{v}</h1></div>'

with tab5:
    st.subheader("📈 Resultados")
    k1,k2,k3,k4,k5=st.columns(5)
    with k1:st.markdown(kpi("MB $/ha",fmd(mb_ha),"kpi-card kpi-negative" if mb_ha<0 else "kpi-card kpi-green"),unsafe_allow_html=True)
    with k2:st.markdown(kpi("MB $/vaca",fmd(mb_vaca),"kpi-card kpi-negative" if mb_vaca<0 else "kpi-card kpi-green"),unsafe_allow_html=True)
    with k3:st.markdown(kpi("Prod kg/ha",fm(kg_ha,1)),unsafe_allow_html=True)
    with k4:st.markdown(kpi("% Destete",fmp(pct_destete_efect)),unsafe_allow_html=True)
    with k5:st.markdown(kpi("Carga",fm(carga,2)),unsafe_allow_html=True)
    st.markdown("")
    if sup_total>0 and vientres>0:
        if balance_ev<0:st.markdown(f'<div class="alert-red">⚠️ EXCEDE — Rodeo: {fm(ev_rodeo,1)} EV / Cap: {fm(ev_capacidad,1)} EV</div>',unsafe_allow_html=True)
        else:st.markdown(f'<div class="alert-green">✅ OK — Rodeo: {fm(ev_rodeo,1)} EV / Cap: {fm(ev_capacidad,1)} EV</div>',unsafe_allow_html=True)
    co1,co2=st.columns(2)
    with co1:
        st.markdown("**Indicadores Físicos**")
        st.dataframe(pd.DataFrame({'Ind.':['Superficie','Vientres','Carga','% Destete','Destetados','Retenidas','Para venta','Producción'],'Valor':[f"{fm(sup_total)} ha",f"{fm(vientres)} cab",f"{fm(carga,2)} vac/ha",fmp(pct_destete_efect),fm(terneros_destetados),fm(reposicion_hembras),fm(terneros_venta),f"{fm(kg_ha,1)} kg/ha"]}),use_container_width=True,hide_index=True)
    with co2:
        st.markdown("**Resultado Económico**")
        rr=[('Ing.Bruto Ventas',ing_bruto),('Gtos.Comerc.',-gtos_ventas),('Ing.Neto Ventas',ing_neto_v),('Repos.Toros',-costo_repos),('ING.NETO TOTAL',ing_neto_total),('Costos Directos',-cd_sin_rep),('MARGEN BRUTO',mb)]
        st.dataframe(pd.DataFrame([{'Concepto':k,'$/año':fmd(v),'$/ha':fmd(v/sup_total) if sup_total>0 else "-"} for k,v in rr]),use_container_width=True,hide_index=True)
    st.markdown("---");st.markdown("**Eficiencia**")
    e1,e2,e3,e4=st.columns(4)
    e1.metric("MB/CD",fm(mb_cd,2));e2.metric("Costo Unit.",f"{fmd(c_unit)}/kg");e3.metric("Precio Neto",f"{fmd(p_neto)}/kg");e4.metric("Pto.Equil.",f"{fm(pto_eq)} tern.")
    if ing_bruto>0 or cd_sin_rep>0:
        wf_x=['Ing.Tern.','Ing.Ref.','Repos.','Alim.','San.','Pers.','Otros','Forr.']
        wf_y=[ing_tern*(1-gtos_com_venta),(ing_vac+ing_tor+ing_vaq)*(1-gtos_com_venta),-costo_repos,-c_alim,-c_san,-c_pers,-c_otros,-costo_forrajero_total]
        if c_arriendo>0:wf_x.append('Arriendo');wf_y.append(-c_arriendo)
        wf_x.append('MB');wf_y.append(0)
        fw=go.Figure(go.Waterfall(x=wf_x,y=wf_y,measure=['relative']*(len(wf_x)-1)+['total'],increasing=dict(marker=dict(color='#27ae60')),decreasing=dict(marker=dict(color='#e74c3c')),totals=dict(marker=dict(color='#2e86c1'))))
        fw.update_layout(title="Cascada MB",height=450,showlegend=False);st.plotly_chart(fw,use_container_width=True)

with tab6:
    st.subheader("🔄 Sensibilidad")
    co1,co2=st.columns(2)
    pvars=np.array([-.30,-.20,-.10,0,.10,.20,.30]);dvars=np.array([-.15,-.10,-.05,0,.05,.10,.15])
    prices=precio_ternero*(1+pvars);destetes=pct_destete_efect+dvars
    z1=np.zeros((7,7))
    for i,d in enumerate(destetes):
        for j,p in enumerate(prices):
            nv=max(0,round(vientres*max(0,d))-reposicion_hembras)
            z1[i,j]=((nv*peso_destete*p*(1-gtos_com_venta)+(ing_vac+ing_tor+ing_vaq)*(1-gtos_com_venta)-costo_repos-cd_sin_rep)/sup_total) if sup_total>0 else 0
    cvars=np.array([-.15,-.10,-.05,0,.05,.10,.15]);svars=np.array([-.30,-.20,-.10,0,.10,.20,.30])
    cargas_s=carga*(1+cvars);supls_s=c_alim*(1+svars)
    z2=np.zeros((7,7))
    for i,s in enumerate(supls_s):
        for j,cg in enumerate(cargas_s):
            nv2=round(cg*sup_total);ntd=round(nv2*pct_destete_efect)
            nrh=round(nv2/vu_vacas+nv2*mort_vacas) if vu_vacas>0 else 0;ntv=max(0,ntd-nrh)
            z2[i,j]=((ntv*peso_destete*precio_ternero*(1-gtos_com_venta)+(ing_vac+ing_tor+ing_vaq)*(1-gtos_com_venta)-costo_repos-s-c_san-c_pers-c_otros-costo_forrajero_total-c_arriendo)/sup_total) if sup_total>0 else 0
    with co1:
        st.markdown("**Precio × Destete → MB $/ha**")
        fs1=go.Figure(data=go.Heatmap(z=z1,x=[fmd(p) for p in prices],y=[fmp(d) for d in destetes],colorscale=[[0,'#e74c3c'],[0.5,'#ffffbf'],[1,'#27ae60']],zmid=0,text=[[fm(z1[i,j]) for j in range(7)] for i in range(7)],texttemplate="%{text}",textfont=dict(size=11)))
        fs1.update_layout(xaxis_title="Precio ($/kg)",yaxis_title="% Destete",height=500);st.plotly_chart(fs1,use_container_width=True)
    with co2:
        st.markdown("**Carga × Suplem. → MB $/ha**")
        fs2=go.Figure(data=go.Heatmap(z=z2,x=[fm(c,2) for c in cargas_s],y=[fmd(s) for s in supls_s],colorscale=[[0,'#e74c3c'],[0.5,'#ffffbf'],[1,'#27ae60']],zmid=0,text=[[fm(z2[i,j]) for j in range(7)] for i in range(7)],texttemplate="%{text}",textfont=dict(size=11)))
        fs2.update_layout(xaxis_title="Carga (vac/ha)",yaxis_title="Costo Suplem.",height=500);st.plotly_chart(fs2,use_container_width=True)

st.divider();st.subheader("📄 Exportar PDF")
caso_nombre=st.text_input("Nombre del caso:","")
if st.button("📥 Generar PDF",type="primary"):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.lib.colors import HexColor,white
    from reportlab.platypus import SimpleDocTemplate,Table,TableStyle,Spacer,Paragraph,Image as RLImage
    from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
    buf=BytesIO();doc=SimpleDocTemplate(buf,pagesize=A4,leftMargin=1.5*cm,rightMargin=1.5*cm,topMargin=1.5*cm,bottomMargin=2.5*cm)
    sty=getSampleStyleSheet();sty.add(ParagraphStyle('T',parent=sty['Title'],fontSize=18,textColor=HexColor('#1a5276'),spaceAfter=6))
    sty.add(ParagraphStyle('S',parent=sty['Normal'],fontSize=11,textColor=HexColor('#555'),spaceAfter=12))
    sty.add(ParagraphStyle('H',parent=sty['Heading2'],fontSize=13,textColor=HexColor('#1a5276'),spaceBefore=16,spaceAfter=8))
    el=[];BM=HexColor('#2e86c1');BL=HexColor('#d6e4f0');GN=HexColor('#27ae60');RD=HexColor('#e74c3c');GL=HexColor('#f5f5f5')
    def mkt(data,cw=None):
        t=Table(data,colWidths=cw,repeatRows=1)
        sc=[('FONTNAME',(0,0),(-1,-1),'Helvetica'),('FONTSIZE',(0,0),(-1,-1),8),('ALIGN',(1,0),(-1,-1),'CENTER'),('ALIGN',(0,0),(0,-1),'LEFT'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('GRID',(0,0),(-1,-1),0.5,HexColor('#ccc')),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),('BACKGROUND',(0,0),(-1,0),BM),('TEXTCOLOR',(0,0),(-1,0),white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold')]
        for i in range(2,len(data),2):sc.append(('BACKGROUND',(0,i),(-1,i),GL))
        t.setStyle(TableStyle(sc));return t
    li=RLImage(LOGO_PATH,width=2.5*cm,height=2.5*cm) if os.path.exists(LOGO_PATH) else ''
    ct1=Paragraph("Ing.Zoot.Esp. José Humberto García | Tel: +54 9 3816021380",ParagraphStyle('c1',parent=sty['Normal'],fontSize=7,alignment=2,textColor=HexColor('#333')))
    ct2=Paragraph("josehumbertogarcia91@gmail.com",ParagraphStyle('c2',parent=sty['Normal'],fontSize=7,alignment=2,textColor=HexColor('#333')))
    ht=Table([[li,Paragraph("SIMULADOR DE CRÍA",sty['T']),Table([[ct1],[ct2]],colWidths=[6*cm])]],colWidths=[3*cm,8.5*cm,6*cm])
    ht.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE')]));el.append(ht)
    if caso_nombre:el.append(Paragraph(f"Caso: {caso_nombre}",sty['S']))
    el.append(Paragraph(f"Fecha: {date.today().strftime('%d/%m/%Y')}",sty['S']));el.append(Spacer(1,6))
    el.append(Paragraph("Indicadores Clave",sty['H']))
    kd=[['MB $/ha','MB $/vaca','Prod kg/ha','% Destete','Carga'],[fmd(mb_ha),fmd(mb_vaca),fm(kg_ha,1),fmp(pct_destete_efect),fm(carga,2)]]
    kt=Table(kd,colWidths=[3.4*cm]*5);MBC=GN if mb_ha>=0 else RD
    kt.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),BM),('TEXTCOLOR',(0,0),(-1,0),white),('FONTNAME',(0,0),(-1,-1),'Helvetica-Bold'),('FONTSIZE',(0,1),(-1,1),12),('ALIGN',(0,0),(-1,-1),'CENTER'),('GRID',(0,0),(-1,-1),1,white),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('BACKGROUND',(0,1),(1,1),MBC),('TEXTCOLOR',(0,1),(1,1),white),('BACKGROUND',(2,1),(-1,1),BL)]));el.append(kt);el.append(Spacer(1,4))
    if sup_total>0 and vientres>0:
        txt=f"⚠ EXCEDE — {fm(ev_rodeo,1)}/{fm(ev_capacidad,1)} EV" if balance_ev<0 else f"✓ OK — {fm(ev_rodeo,1)}/{fm(ev_capacidad,1)} EV"
        bg=HexColor('#f8d7da') if balance_ev<0 else HexColor('#d4edda');tc2=HexColor('#721c24') if balance_ev<0 else HexColor('#155724');bx=RD if balance_ev<0 else GN
        at=Table([[txt]],colWidths=[17*cm]);at.setStyle(TableStyle([('BACKGROUND',(0,0),(0,0),bg),('TEXTCOLOR',(0,0),(0,0),tc2),('FONTNAME',(0,0),(0,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(0,0),9),('ALIGN',(0,0),(0,0),'CENTER'),('BOX',(0,0),(0,0),1.5,bx),('TOPPADDING',(0,0),(0,0),6),('BOTTOMPADDING',(0,0),(0,0),6)]));el.append(at)
    el.append(Spacer(1,8));el.append(Paragraph("Planteo Forrajero",sty['H']))
    fr=[['Recurso','Sup','EV/ha','Mes','Sup.Ef.','Cap.EV']]
    for n,r in recursos.items():
        if r['sup']>0:fr.append([n,fm(r['sup']),fm(r['recep'],1),fm(r['meses']),fm(r['sup']*r['meses']/12,1),fm(r['sup']*r['recep']*r['meses']/12,1)])
    fr.append(['TOTAL',fm(sup_total),'','',fm(sup_efectiva,1),fm(ev_capacidad,1)])
    if len(fr)>2:el.append(mkt(fr,[4*cm,2.2*cm,2*cm,1.5*cm,2.5*cm,2.5*cm]))
    el.append(Spacer(1,8));el.append(Paragraph("Cadena Reproductiva",sty['H']))
    el.append(mkt([['Etapa','Cab','Ind.'],['Entorados',fm(vientres),''],['Preñadas',fm(vacas_prenadas),fmp(pct_prenez)],['Nacidos',fm(terneros_nacidos),fmp(pct_paricion)],['Destetados',fm(terneros_destetados),fmp(1-pct_perdidas)],['Retenidas',fm(reposicion_hembras),'Repos.'],['Venta',fm(terneros_venta),f'Dest:{fmp(pct_destete_efect)}']],[5*cm,3*cm,5*cm]))
    el.append(Spacer(1,8));el.append(Paragraph("Resultado Económico",sty['H']))
    er=[['Concepto','$/año','$/ha','$/vaca'],['Ing.Bruto',fmd(ing_bruto),fmd(ing_bruto/sup_total) if sup_total else '-',fmd(ing_bruto/vientres) if vientres else '-'],['Gtos.Com.',f'-{fmd(gtos_ventas)}','',''],['Ing.Neto V.',fmd(ing_neto_v),'',''],['Repos.',f'-{fmd(costo_repos)}','',''],['Ing.Neto T.',fmd(ing_neto_total),'',''],['Aliment.',f'-{fmd(c_alim)}','',''],['Sanidad',f'-{fmd(c_san)}','',''],['Personal',f'-{fmd(c_pers)}','','']]
    if c_arriendo>0:er.append(['Arriendo',f'-{fmd(c_arriendo)}','',''])
    er.append(['Otros+Forr.',f'-{fmd(c_otros+costo_forrajero_total)}','',''])
    er.append(['MARGEN BRUTO',fmd(mb),fmd(mb_ha),fmd(mb_vaca)])
    et=mkt(er,[5*cm,3.5*cm,3.5*cm,3.5*cm]);MBG=HexColor('#c6efce') if mb>=0 else HexColor('#ffc7ce')
    et.setStyle(TableStyle([('BACKGROUND',(0,len(er)-1),(-1,len(er)-1),MBG),('FONTNAME',(0,len(er)-1),(-1,len(er)-1),'Helvetica-Bold'),('FONTSIZE',(0,len(er)-1),(-1,len(er)-1),10)]));el.append(et)
    el.append(Spacer(1,8));el.append(Paragraph("Eficiencia",sty['H']))
    el.append(mkt([['Indicador','Valor'],['MB/CD',fm(mb_cd,2)],['Costo unit.',f'{fmd(c_unit)}/kg'],['Precio neto',f'{fmd(p_neto)}/kg'],['Pto.equil.',f'{fm(pto_eq)} tern.'],['Producción',f'{fm(kg_ha,1)} kg/ha']],[6*cm,4*cm]))
    el.append(Spacer(1,8));el.append(Paragraph("Sensibilidad: Precio × Destete (MB $/ha)",sty['H']))
    s1=[['D/P']+[fmd(p) for p in prices]]
    for i,d in enumerate(destetes):s1.append([fmp(d)]+[fmd(z1[i,j]) for j in range(7)])
    st1=mkt(s1,[2.3*cm]+[2.1*cm]*7);scc=[]
    for i in range(7):
        for j in range(7):scc.append(('BACKGROUND',(j+1,i+1),(j+1,i+1),HexColor('#c6efce') if z1[i,j]>=0 else HexColor('#ffc7ce')))
    st1.setStyle(TableStyle(scc));el.append(st1)
    el.append(Spacer(1,8));el.append(Paragraph("Sensibilidad: Carga × Suplem. (MB $/ha)",sty['H']))
    s2=[['S/C']+[fm(c,2) for c in cargas_s]]
    for i,s in enumerate(supls_s):s2.append([fmd(s)]+[fmd(z2[i,j]) for j in range(7)])
    st2=mkt(s2,[2.3*cm]+[2.1*cm]*7);scc2=[]
    for i in range(7):
        for j in range(7):scc2.append(('BACKGROUND',(j+1,i+1),(j+1,i+1),HexColor('#c6efce') if z2[i,j]>=0 else HexColor('#ffc7ce')))
    st2.setStyle(TableStyle(scc2));el.append(st2)
    doc.build(el)
    st.download_button("⬇️ Descargar PDF",buf.getvalue(),f"reporte_cria_{caso_nombre.replace(' ','_') if caso_nombre else 'sim'}_{date.today().strftime('%Y%m%d')}.pdf","application/pdf")
    st.success("✅ PDF generado")

st.divider();st.markdown('<div style="text-align:center;color:#888;font-size:0.85rem;">Simulador de Cría · Don Tito</div>',unsafe_allow_html=True)
