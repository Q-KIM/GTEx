# Detect eQTL by dynamic slicing.
# Songpeng Zu
# 2015-02-27

# Gene Expression Data by Zhirui Hu.

#-- load the libraries
library(Rcpp) # used for DECODE
library(dynslicing) # used for DECODE
library(data.table) # used for loading big data
library(stringr) # used for getSampleIds

#-- Supplementary Data Directory 
supdir <- "/n/home00/szu/KR_eQTL/GTex"

#-- Get the input parameters.
args <- commandArgs(trailingOnly = TRUE)

# The start/end point is only dependent on genelocsnp data.
# They should be the same across different tissues.
gene_residual <- fread(args[1],header=TRUE) # Read gene residuals' matrix, full path needed.
startpoint <- strtoi(args[2]) # gene lable start 
endpoint <- strtoi(args[3]) # gene lable end
tissuenm <- args[4]

#--Define outputfile name.
outdir <- "/n/home00/szu/gtex"
outfilename <- paste(paste(outdir,tissuenm,sep="/"),startpoint,endpoint,sep="_")

#-- Get the genes' name, samples' name and gene_residual_matrix
gene_samplenm <- colnames(gene_residual)[2:ncol(gene_residual)]
genenm <- gene_residual[,1,with=FALSE]
gene_residual_matrix <- as.matrix(gene_residual[1:nrow(gene_residual),2:ncol(gene_residual),with=FALSE])
dimnames(gene_residual_matrix) <- list(genenm,gene_samplenm)
rm(gene_residual)

# FUNCTION of extracting SNP samples' names from gene_samplenm.
getSNPsampleIds <- function(genenmstr){
    m = str_match_all(genenmstr,'(^G.*)\\.[0-9]{4}')
    return(m[[1]][2])
}
gene2snp_samplenm <- unlist(apply(as.matrix(gene_samplenm),getSNPsampleIds))

#-- Get the snps' name, samples' name and snp_value_matrix
snp_samplenm <- as.matrix(read.table(paste(supdir,"GTEx.SNP.sampleID",sep="/")) 
snp_value <- fread(paste(supdir,"GTEx.wholegenome.SNP",sep="/"))
snp_value_matrix <- as.matrix(snp_value[ ,2:ncol(snp_value),with=FALSE])
dimnames(snp_value_matrix) <- list(snp_value$V1, snp_samplenm[ ,1])
rm(snp_value)

#-- Reorganize both of the matrix based on the samples' ID.
cosamplenm <- intersect(gene2snp_samplenm,colnames(snp_value_matrix))
gene_re_matrix <- gene_residual_matrix[ ,cosamplenm]
rm(gene_residual_matrix)
snp_re_matrix <- snp_value_matrix[ ,cosamplenm]
rm(snp_value_matrix)

#-- FUNCTION of DECODE 
eqtlDECODE <- function(genestarnm,geneendnm){
    # Load gene-snp relationship information
    gene2snptotal <- fread(paste(supdir,"genelocsnp",sep="/"),header=FALSE,sep="\n")
    getgene2snp <- function(index1,index2){
        List <- list()
        for(i in index1:index2){
            myVector <- strsplit(as.character(gene2snptotal[i,]),"\t")
            tmplist <- list(myVector[[1]][2:length(myVector[[1]] )] )
            names(tmplist) <- myVecotr[[1]][1]
            List[[length(List)+1]] <- tmplist
        }
        return(List)
    }
    gene2snp <- getgene2snp(genestarnm,geneendnm)
    rm(gene2snptotal)
    
    # Get the final genes with genelocsnp and gene residual information.
    genearray <- as.matrix(intersect(names(gene2snp),genenm))

    # FUNCTION Of DECODE for single gene.
    eqtlDECODEsingle <- function(singlenm){
        # The singlenm should be in the gene_residual_matrix.
        genearray <- gene_re_matrix[singlenm, ]
        # The singlenm should also be in the gene2snp.
        snparray <- snp_re_matrix[gene2snp[[singlenm]], ]
        snparray_order <- snparray[ ,order(genearray)]
        rm(snparray)
        # Set the parameters.
        dim <- 3 # The categories of SNPs.(0,1,2)
        lambda <- 1.0
        alpha <- 1.0
        decode_values <- apply(snparray_order,1,function(x) ds_bf_u(x[!is.na(x)],dim,lambda,alpha))
        cat(paste(c(singlenm,decode_values),collapse="\t"),file=outfilename,sep="\n",append=TRUE)
    }
    # apply the eqtlDECODEsingle function.
    apply(genearray,1,function(x) eqtlDECODEsingle(x))
}

#-- Main Function
eqtlDECODE(genestartnm,geneendnm)




