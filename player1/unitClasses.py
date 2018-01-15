import battlecode as bc

#try calculating best directions for each start

#heuristic
def chessDist(pt1,pt2):
    return max(abs(pt1[0]-pt2[0]),abs(pt1[1]-pt2[1]))

def getAStarPath(map,start,goal):
