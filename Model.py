import numpy as np

from EconModel import EconModelClass

woman = 1
man = 2

class ModelClass(EconModelClass):
    
    def settings(self):
        """ fundamental settings """
        pass
        
    def setup(self):
        """ set baseline parameters """
        par = self.par

        ###########
        # utility #
        par.delta = 1.0 # value of spending time with child
        
        ###################
        # state variables #
        
        # net migration return
        par.num_R = 100

        par.max_R = 20.0
        par.min_R = -20.0

        # share with mother
        par.num_share = 20

        par.min_share = 0.0
        par.max_share = 1.0
        
    def allocate(self):
        par = self.par
        sol = self.sol

        # a. setup grids
        self.setup_grids()

        # b. memory for solution
        shape_couple = (par.num_R,par.num_R)
        sol.move_couple_w = np.zeros(shape_couple,dtype=bool) 
        sol.move_couple_m = np.zeros(shape_couple,dtype=bool) 

        shape_divorced = (par.num_share,par.num_R,par.num_R)
        sol.move_joint_w = np.zeros(shape_divorced,dtype=bool)  
        sol.move_joint_m = np.zeros(shape_divorced,dtype=bool)  

        sol.move_sole_w = np.zeros(shape_divorced,dtype=bool)  
        sol.move_sole_m = np.zeros(shape_divorced,dtype=bool)  
        
        
    def setup_grids(self):
        par = self.par
        
        # a. net return from migration
        par.grid_R = np.linspace(par.min_R,par.max_R,par.num_R) 
        par.grid_Rw,par.grid_Rm = np.meshgrid(par.grid_R,par.grid_R,indexing='ij')

        # b. share with mother
        par.grid_share = np.linspace(par.min_share,par.max_share,par.num_share)


    def solve(self):
        sol = self.sol
        par = self.par 

        # Loop through all potential combinations of returns
        for i_Rw,Rw in enumerate(par.grid_R):
            for i_Rm,Rm in enumerate(par.grid_R):
               
                # couple
                sol.move_couple_w[i_Rw,i_Rm] , sol.move_couple_m[i_Rw,i_Rm] = self.optimal_move_couple(Rw,Rm,par)
                
                # divorced with children. Loop through all possible sharing rules
                for i_share,share_w in enumerate(par.grid_share):
                    idx = (i_share,i_Rw,i_Rm)
                    
                    # joint custody
                    sol.move_joint_w[idx] , sol.move_joint_m[idx] = self.optimal_move_joint_custody(Rw,Rm,share_w,par)

                    # sole custody to mother
                    sol.move_sole_w[idx] , sol.move_sole_m[idx] = self.optimal_move_sole_custody(Rw,Rm,share_w,par)


    def optimal_move_single(self,R,par):
        """ optimal move for a single person """
        move = R > 0
        return move

    def optimal_move_couple(self,Rw,Rm,par):
        """ optimal move for a couple: r_w, r_m """

        move = (Rw + Rm) > 0 #Transferable utility
        return move,move
    
    def optimal_move_joint_custody(self,Rw,Rm,share_w,par):
        """ optimal move for a couple with joint custody: r_w, r_m """
        
        move_w = False
        move_m = False

        # both benefit
        if (Rw>0) and (Rm>0): # both benefit
            move_w = True
            move_m = True
        
        else:
            if Rm > (1.0-share_w) * par.delta: # father benefits enough to move w.o. child
                move_m = True

            if Rw > share_w * par.delta: # mother benefits enough to move w.o. child
                move_w = True

        return move_w,move_m
    
    def optimal_move_sole_custody(self,Rw,Rm,share_w,par):
        """ optimal move for a couple with mother having sole custody: r_w, r_m """
        
        move_w = Rw > 0 # child will follow custodial parent (mother)

        share_father = (1.0 - share_w) * par.delta
        move_m = False
        if move_w:
            move_m = Rm > - share_father # if he does not follow the mother, he will lose time with the child

        else:
            move_m = Rm > share_father
        
        return move_w,move_m

    # NOT USED NOW
    def util(self,R,share_w,move,child_move,sex,par):
        """ utility function """

        # a. value of spending time with child
        if move == child_move: # in same place as child
            share = share_w if sex==woman else 1.0-share_w
            util_child = share * par.delta

        else: # not in same place as child
            util_child = 0.0

        # b. utility from moving
        util_move = R * move

        # c. total
        return util_move + util_child

        

    