import maya.cmds as cmds

selectedJoints = cmds.ls(selection=True)
first_sel = selectedJoints[0]
last_sel = selectedJoints[1]

get_selected_joints = cmds.ls(selectedJoints[1], l=True)[0].split("|")

first_sel_indx = get_selected_joints.index(selectedJoints[0])
last_sel_indx = get_selected_joints.index(selectedJoints[1])

joints_for_curve = get_selected_joints[first_sel_indx:]
n_joints_points = len(joints_for_curve)

pos_list = []
for sel in joints_for_curve:
    pos = cmds.xform(sel,q=1,ws=1,rp=1)
    pos_list.append(tuple(pos))
    

bottom = selectedJoints[0]
upper = selectedJoints[1]

ikh,effector_obj,curve_obj = cmds.ikHandle(name="ikSpline_customG",sj=str(bottom), ee=str(upper), sol="ikSplineSolver",pcv=True, ccv=True, tws="easeInOut" )

curve_obj = cmds.rename(curve_obj,"spline_curve_customG")

#joint bind to curve
jtb_hips = cmds.duplicate(bottom, po=True)
jtb_hips = cmds.rename(jtb_hips[0],"jtb_hips_customG")

jtb_shoulders = cmds.duplicate(upper, po=True)
jtb_shoulders = cmds.rename(jtb_shoulders[0], "jtb_shoulders_customG")
jtb_shoulders_parent = cmds.listRelatives(jtb_shoulders,p=True)
cmds.parent(jtb_shoulders,world=True)

cmds.select(curve_obj)
cmds.select(jtb_hips,add=True)
cmds.select(jtb_shoulders,add=True)

cmds.skinCluster(tsb=True)

jtb_hips_pos = cmds.xform(jtb_hips,q=1,ws=1,rp=1)
jtb_shoulders_pos = cmds.xform(jtb_shoulders,q=1,ws=1,rp=1)

#Hips controller: create and clean
hips_ctrl = cmds.circle(n="hips_ctrl_customG",nr=(0, 1, 0), c=(0, 0, 0))
cmds.move( jtb_hips_pos[0], jtb_hips_pos[1], jtb_hips_pos[2], hips_ctrl, absolute=True )
cmds.scale( 35, 35, 35, hips_ctrl, absolute=True )
cmds.makeIdentity(hips_ctrl, apply=True, t=1, r=1, s=1, n=2 )
cmds.delete(hips_ctrl, constructionHistory = True)

#chest controller: create and clean
chest_ctrl = cmds.circle(n="chest_ctrl_customG",nr=(0, 1, 0), c=(0, 0, 0))
cmds.move( jtb_shoulders_pos[0], jtb_shoulders_pos[1], jtb_shoulders_pos[2], chest_ctrl, absolute=True )
cmds.scale( 25, 25, 25, chest_ctrl, absolute=True )
cmds.makeIdentity(chest_ctrl, apply=True, t=1, r=1, s=1, n=2 )
cmds.delete(chest_ctrl, constructionHistory = True)

#parent joint to controller
cmds.parent(jtb_hips,hips_ctrl[0])
cmds.parent(jtb_shoulders,chest_ctrl[0])
cmds.parent(chest_ctrl[0],hips_ctrl[0])


def parent_obj(top,children):
   
       if len(children) != 1:
           new_top = cmds.parent(children[1:],top)
           children = cmds.listRelatives(new_top, c=True)
           print new_top
           parent_obj(new_top,children)
       else:
           return
       
 
    
result = cmds.promptDialog(
                title='Spine Control',
                message='Choose a joint:',
                button=['OK', 'Cancel'],
                defaultButton='OK',
                cancelButton='Cancel',
                dismissString='Cancel',text=",".join(joints_for_curve[1:-1]))

if result == 'OK':
        text = cmds.promptDialog(query=True, text=True)
        joints_to_chose = list(str(text).split(','))
        
        spine_controllers = []
        for joints in joints_to_chose:

            joint_ctrl = cmds.circle(n=str(joints+"_ctrl_customG"),nr=(0, 1, 0), c=(0, 0, 0))
            
            joint_pos = cmds.xform(joints,q=1,ws=1,rp=1)
            
            cmds.move( joint_pos[0], joint_pos[1], joint_pos[2], joint_ctrl, absolute=True )
            cmds.scale( 25, 25, 25, joint_ctrl, absolute=True )
            cmds.makeIdentity(joint_ctrl, apply=True, t=1, r=1, s=1, n=2 )
            cmds.delete(joint_ctrl, constructionHistory = True)
            
            
            spine_controllers.append(joint_ctrl[0])
            
        parent_obj(spine_controllers[0],spine_controllers)
        
        n_spine_ctrl = len(spine_controllers)
        
        cmds.parent(spine_controllers[0],hips_ctrl[0])
        cmds.parent(chest_ctrl[0],spine_controllers[n_spine_ctrl-1])
        
#Spline IK Advanced twist
ikSplines = cmds.ls(type="ikHandle")

for ikSpline in ikSplines:
    if "_customG" in ikSpline:
        cmds.setAttr( str(ikSpline+'.dTwistControlEnable'), True)
        cmds.setAttr( str(ikSpline+'.dWorldUpType'), 4)
        cmds.setAttr( str(ikSpline+'.dForwardAxis'), 0)
        cmds.setAttr( str(ikSpline+'.dWorldUpAxis'), 4)
        cmds.setAttr( str(ikSpline+'.dWorldUpVectorY'), 0)
        cmds.setAttr( str(ikSpline+'.dWorldUpVectorEndY'), 0)
        cmds.setAttr( str(ikSpline+'.dWorldUpVectorZ'), -1)
        cmds.setAttr( str(ikSpline+'.dWorldUpVectorEndZ'), -1)
        cmds.connectAttr(str(hips_ctrl[0]+".worldMatrix[0]"),str(ikSpline+'.dWorldUpMatrix'),force=True)
        cmds.connectAttr(str(chest_ctrl[0]+".worldMatrix[0]"),str(ikSpline+'.dWorldUpMatrixEnd'),force=True)            
