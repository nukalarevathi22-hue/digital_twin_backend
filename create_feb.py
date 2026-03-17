# create_feb_file.py
feb_content = '''<?xml version="1.0" encoding="UTF-8"?>
<febio_spec version="4.0">
  <Module type="fluid"/>
  <Module type="FSI"/>
  
  <Control>
    <title>Cardiac FSI Simulation - Left Ventricle</title>
    <time_steps>100</time_steps>
    <step_size>0.01</step_size>
    <solver>
      <max_refs>15</max_refs>
      <max_ups>10</max_ups>
      <diverge_reform>1</diverge_reform>
      <reform_each_time_step>1</reform_each_time_step>
      <dtol>0.001</dtol>
      <etol>0.01</etol>
      <rtol>0.001</rtol>
      <lstol>0.9</lstol>
      <min_residual>1e-20</min_residual>
    </solver>
    <time_stepper>
      <dtmin>0.001</dtmin>
      <dtmax>0.05</dtmax>
      <max_retries>5</max_retries>
      <opt_iter>10</opt_iter>
    </time_stepper>
    <analysis type="dynamic"/>
    <plot_level>PLOT_MAJOR_ITRS</plot_level>
    <output>
      <plotfile type="febio">
        <var type="displacement"/>
        <var type="stress"/>
        <var type="fluid pressure"/>
        <var type="fluid velocity"/>
        <var type="relative volume"/>
      </plotfile>
    </output>
  </Control>

  <Globals>
    <Constants>
      <T>0</T>
      <R>0</R>
      <Fc>0</Fc>
    </Constants>
  </Globals>

  <Material>
    <material id="1" name="myocardium" type="orthotropic elastic">
      <density>1.0</density>
      <elastic>
        <E1>100</E1>
        <E2>100</E2>
        <E3>50</E3>
        <v12>0.4</v12>
        <v23>0.4</v23>
        <v31>0.4</v31>
        <G12>30</G12>
        <G23>30</G23>
        <G31>30</G31>
      </elastic>
    </material>
    
    <material id="2" name="active_contraction" type="active contraction">
      <activation>0.1</activation>
      <max_tension>100</max_tension>
      <T0>0.2</T0>
      <Tmax>0.5</Tmax>
    </material>
    
    <material id="3" name="blood" type="Newtonian fluid">
      <density>1.06</density>
      <viscosity>0.04</viscosity>
    </material>
  </Material>

  <Geometry>
    <Nodes>
      <node id="1"> 0.0, 0.0, 0.0</node>
      <node id="2"> 3.0, 0.0, 0.0</node>
      <node id="3"> 0.0, 2.0, 0.0</node>
      <node id="4">-3.0, 0.0, 0.0</node>
      <node id="5"> 0.0,-2.0, 0.0</node>
      <node id="6"> 0.0, 0.0, 5.0</node>
      <node id="7"> 2.0, 0.0, 5.0</node>
      <node id="8"> 0.0, 1.5, 5.0</node>
      <node id="9">-2.0, 0.0, 5.0</node>
      <node id="10">0.0,-1.5, 5.0</node>
    </Nodes>

    <Elements>
      <solid mat="1" el_type="penta6">
        <elem id="1">1,2,3,6,7,8</elem>
        <elem id="2">1,3,4,6,8,9</elem>
        <elem id="3">1,4,5,6,9,10</elem>
        <elem id="4">1,5,2,6,10,7</elem>
      </solid>
      
      <fluid mat="3" el_type="penta6">
        <elem id="5">2,7,7,3,8,8</elem>
        <elem id="6">3,8,8,4,9,9</elem>
        <elem id="7">4,9,9,5,10,10</elem>
        <elem id="8">5,10,10,2,7,7</elem>
      </fluid>
    </Elements>

    <Surface>
      <Surface name="endocardium" type="element">
        <elem_surface>5,0</elem_surface>
        <elem_surface>6,0</elem_surface>
        <elem_surface>7,0</elem_surface>
        <elem_surface>8,0</elem_surface>
      </Surface>
    </Surface>
  </Geometry>

  <Boundary>
    <fix dof="x y z">1,2,3,4,5</fix>
    
    <pressure type="fluid" surface="endocardium">
      <scale lc="1">10.0</scale>
    </pressure>
  </Boundary>

  <Loads>
    <loadcurve id="1" type="linear">
      <point>0,0</point>
      <point>0.5,10</point>
      <point>1.0,5</point>
    </loadcurve>
  </Loads>

  <Contact>
    <fsi type="fluid-solid" surface_pair="endocardium">
      <tolerance>0.01</tolerance>
      <penalty>1000</penalty>
    </fsi>
  </Contact>
</febio_spec>'''

with open('cardiac_fsi_complete.feb', 'w') as f:
    f.write(feb_content)

print("✅ Created cardiac_fsi_complete.feb file")